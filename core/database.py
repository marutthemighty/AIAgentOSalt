import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Text, DateTime, Boolean, Integer
from sqlalchemy.exc import SQLAlchemyError
import sqlite3

class DatabaseManager:
    """
    Manages database connections for both online (Supabase) and offline (SQLite) modes
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.engine = None
        self.metadata = MetaData()
        self.is_online = False
        
        # Initialize database connection
        self._initialize_connection()
        self._create_tables()
    
    def _initialize_connection(self):
        """Initialize database connection (Supabase or SQLite fallback)"""
        try:
            # Try Supabase connection first
            database_url = os.getenv('DATABASE_URL')
            if database_url and 'supabase' in database_url:
                self.engine = create_engine(database_url)
                # Test connection
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                self.is_online = True
                self.logger.info("Connected to Supabase database")
                return
        except Exception as e:
            self.logger.warning(f"Failed to connect to Supabase: {str(e)}")
        
        try:
            # Fallback to local SQLite
            db_path = os.path.join(os.getcwd(), 'creative_workflow.db')
            self.engine = create_engine(f'sqlite:///{db_path}')
            self.is_online = False
            self.logger.info("Connected to local SQLite database")
        except Exception as e:
            self.logger.error(f"Failed to connect to any database: {str(e)}")
            raise
    
    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            # Projects table
            projects_table = Table(
                'projects', self.metadata,
                Column('id', String(50), primary_key=True),
                Column('name', String(255), nullable=False),
                Column('client_name', String(255)),
                Column('description', Text),
                Column('status', String(50), default='active'),
                Column('created_at', DateTime, default=datetime.utcnow),
                Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
                Column('metadata', Text)  # JSON field for additional data
            )
            
            # Tasks table
            tasks_table = Table(
                'tasks', self.metadata,
                Column('id', String(50), primary_key=True),
                Column('project_id', String(50)),
                Column('title', String(255), nullable=False),
                Column('description', Text),
                Column('assignee', String(255)),
                Column('status', String(50), default='pending'),
                Column('priority', String(20), default='medium'),
                Column('due_date', DateTime),
                Column('created_at', DateTime, default=datetime.utcnow),
                Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
                Column('metadata', Text)
            )
            
            # Agent executions table
            agent_executions_table = Table(
                'agent_executions', self.metadata,
                Column('id', String(50), primary_key=True),
                Column('agent_name', String(100), nullable=False),
                Column('action', String(255), nullable=False),
                Column('input_data', Text),
                Column('output_data', Text),
                Column('success', Boolean, default=True),
                Column('error_message', Text),
                Column('execution_time', Integer),  # in milliseconds
                Column('timestamp', DateTime, default=datetime.utcnow),
                Column('project_id', String(50)),
                Column('user_id', String(50))
            )
            
            # Client communications table
            client_communications_table = Table(
                'client_communications', self.metadata,
                Column('id', String(50), primary_key=True),
                Column('project_id', String(50)),
                Column('client_id', String(50)),
                Column('message', Text),
                Column('sentiment_score', Integer),  # -1 to 1 scaled to -100 to 100
                Column('communication_type', String(50)),  # email, slack, meeting, etc.
                Column('timestamp', DateTime, default=datetime.utcnow),
                Column('metadata', Text)
            )
            
            # Deliverables table
            deliverables_table = Table(
                'deliverables', self.metadata,
                Column('id', String(50), primary_key=True),
                Column('project_id', String(50)),
                Column('name', String(255), nullable=False),
                Column('file_path', String(500)),
                Column('file_type', String(50)),
                Column('version', String(20), default='1.0'),
                Column('status', String(50), default='draft'),
                Column('created_at', DateTime, default=datetime.utcnow),
                Column('metadata', Text)
            )
            
            # Create all tables
            self.metadata.create_all(self.engine)
            self.logger.info("Database tables created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating database tables: {str(e)}")
            raise
    
    def check_connection(self) -> bool:
        """Check if database connection is active"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
    
    def save_project(self, project_data: Dict[str, Any]) -> str:
        """Save a new project"""
        try:
            project_id = self._generate_id()
            
            insert_data = {
                'id': project_id,
                'name': project_data.get('name'),
                'client_name': project_data.get('client_name'),
                'description': project_data.get('description'),
                'status': project_data.get('status', 'active'),
                'metadata': json.dumps(project_data.get('metadata', {}))
            }
            
            with self.engine.connect() as conn:
                conn.execute(
                    text("""
                        INSERT INTO projects (id, name, client_name, description, status, created_at, metadata)
                        VALUES (:id, :name, :client_name, :description, :status, :created_at, :metadata)
                    """),
                    {**insert_data, 'created_at': datetime.utcnow()}
                )
                conn.commit()
            
            self.logger.info(f"Project saved with ID: {project_id}")
            return project_id
            
        except Exception as e:
            self.logger.error(f"Error saving project: {str(e)}")
            raise
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project by ID"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT * FROM projects WHERE id = :project_id"),
                    {'project_id': project_id}
                )
                row = result.fetchone()
                
                if row:
                    return {
                        'id': row.id,
                        'name': row.name,
                        'client_name': row.client_name,
                        'description': row.description,
                        'status': row.status,
                        'created_at': row.created_at,
                        'updated_at': row.updated_at,
                        'metadata': json.loads(row.metadata) if row.metadata else {}
                    }
                return None
        except Exception as e:
            self.logger.error(f"Error getting project: {str(e)}")
            return None
    
    def save_task(self, task_data: Dict[str, Any]) -> str:
        """Save a new task"""
        try:
            task_id = self._generate_id()
            
            with self.engine.connect() as conn:
                conn.execute(
                    text("""
                        INSERT INTO tasks (id, project_id, title, description, assignee, status, priority, due_date, created_at, metadata)
                        VALUES (:id, :project_id, :title, :description, :assignee, :status, :priority, :due_date, :created_at, :metadata)
                    """),
                    {
                        'id': task_id,
                        'project_id': task_data.get('project_id'),
                        'title': task_data.get('title'),
                        'description': task_data.get('description'),
                        'assignee': task_data.get('assignee'),
                        'status': task_data.get('status', 'pending'),
                        'priority': task_data.get('priority', 'medium'),
                        'due_date': task_data.get('due_date'),
                        'created_at': datetime.utcnow(),
                        'metadata': json.dumps(task_data.get('metadata', {}))
                    }
                )
                conn.commit()
            
            return task_id
        except Exception as e:
            self.logger.error(f"Error saving task: {str(e)}")
            raise
    
    def log_agent_execution(self, execution_data: Dict[str, Any]):
        """Log agent execution"""
        try:
            execution_id = self._generate_id()
            
            with self.engine.connect() as conn:
                conn.execute(
                    text("""
                        INSERT INTO agent_executions 
                        (id, agent_name, action, input_data, output_data, success, error_message, execution_time, timestamp, project_id, user_id)
                        VALUES (:id, :agent_name, :action, :input_data, :output_data, :success, :error_message, :execution_time, :timestamp, :project_id, :user_id)
                    """),
                    {
                        'id': execution_id,
                        'agent_name': execution_data.get('agent_name'),
                        'action': execution_data.get('action'),
                        'input_data': json.dumps(execution_data.get('input_data', {})),
                        'output_data': json.dumps(execution_data.get('output_data', {})),
                        'success': execution_data.get('success', True),
                        'error_message': execution_data.get('error_message'),
                        'execution_time': execution_data.get('execution_time'),
                        'timestamp': datetime.utcnow(),
                        'project_id': execution_data.get('project_id'),
                        'user_id': execution_data.get('user_id')
                    }
                )
                conn.commit()
        except Exception as e:
            self.logger.error(f"Error logging agent execution: {str(e)}")
    
    def get_recent_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent agent activity"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT agent_name, action, success, timestamp, error_message
                        FROM agent_executions 
                        ORDER BY timestamp DESC 
                        LIMIT :limit
                    """),
                    {'limit': limit}
                )
                
                activities = []
                for row in result:
                    activities.append({
                        'agent': row.agent_name,
                        'action': row.action,
                        'success': row.success,
                        'timestamp': row.timestamp.strftime('%Y-%m-%d %H:%M:%S') if row.timestamp else '',
                        'details': row.error_message if not row.success else 'Completed successfully'
                    })
                
                return activities
        except Exception as e:
            self.logger.error(f"Error getting recent activity: {str(e)}")
            return []
    
    def save_client_communication(self, comm_data: Dict[str, Any]) -> str:
        """Save client communication with sentiment analysis"""
        try:
            comm_id = self._generate_id()
            
            with self.engine.connect() as conn:
                conn.execute(
                    text("""
                        INSERT INTO client_communications 
                        (id, project_id, client_id, message, sentiment_score, communication_type, timestamp, metadata)
                        VALUES (:id, :project_id, :client_id, :message, :sentiment_score, :communication_type, :timestamp, :metadata)
                    """),
                    {
                        'id': comm_id,
                        'project_id': comm_data.get('project_id'),
                        'client_id': comm_data.get('client_id'),
                        'message': comm_data.get('message'),
                        'sentiment_score': comm_data.get('sentiment_score'),
                        'communication_type': comm_data.get('communication_type'),
                        'timestamp': datetime.utcnow(),
                        'metadata': json.dumps(comm_data.get('metadata', {}))
                    }
                )
                conn.commit()
            
            return comm_id
        except Exception as e:
            self.logger.error(f"Error saving client communication: {str(e)}")
            raise
    
    def _generate_id(self) -> str:
        """Generate unique ID"""
        import uuid
        return str(uuid.uuid4())
