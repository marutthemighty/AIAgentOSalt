# Creative Workflow AI OS

## Overview

The Creative Workflow AI OS is a comprehensive multi-agent system designed to automate creative agency workflows through 12 specialized AI agents. The system processes client communications, generates project briefs, creates taskboards, develops branding materials, and manages the entire creative project lifecycle from initial client contact through final deliverable packaging.

Built with Streamlit for the frontend interface, the application orchestrates AI agents that handle everything from meeting note processing to sentiment analysis, enabling creative agencies to dramatically reduce manual overhead while maintaining high-quality client service.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Streamlit Web Application**: Multi-page interface with dedicated pages for each major workflow component
- **Session State Management**: Centralized state management for orchestrator and database connections
- **Real-time Dashboard**: Agent monitoring with system metrics and health checks
- **Responsive Layout**: Wide layout with expandable sidebar for navigation and control panels

### Backend Architecture
- **Agent Orchestrator Pattern**: Central orchestrator (`AgentOrchestrator`) manages 12 specialized AI agents with message queuing and inter-agent communication
- **Base Agent Framework**: Abstract base class (`BaseAgent`) provides standard interface, health checks, memory management, and message handling for all agents
- **Asynchronous Processing**: Full async/await pattern for concurrent agent operations and AI API calls
- **Memory and Learning**: Agents maintain memory for user preferences and workflow patterns

### Agent Ecosystem
The system implements 12 specialized agents:
- **Meeting Notes Processor**: Converts transcripts to structured action items
- **Creative Brief Parser**: Transforms unstructured client input into structured briefs
- **Taskboard Generator**: Creates actionable project taskboards with assignments
- **Branding Generator**: Generates comprehensive brand kits and messaging
- **Proposal Generator**: Converts briefs into professional proposals with legal scoping
- **Content Plan Generator**: Creates content calendars and SEO strategies
- **Asset Validator**: AI-based quality assurance for deliverables
- **Client Portal Assistant**: Chatbot interface for client communication
- **Deliverables Packager**: Organizes and packages final project assets
- **Analytics Estimator**: Predicts project costs and timelines from historical data
- **Workflow Optimizer**: Analyzes workflow efficiency and suggests improvements
- **Sentiment Analyzer**: Monitors client satisfaction from communications

### Data Storage Solutions
- **Hybrid Database Strategy**: Primary Supabase (PostgreSQL) connection with SQLite fallback for offline operation
- **SQLAlchemy ORM**: Database abstraction layer supporting both PostgreSQL and SQLite
- **Automatic Failover**: Graceful degradation to local SQLite when cloud database is unavailable
- **Structured Schema**: Tables for projects, tasks, agents, client communications, and system metrics

### AI Integration
- **Google Gemini API**: Primary AI service with Gemini 2.5 Flash as default model
- **Fallback Model Strategy**: Automatic fallback to Gemini 2.5 Pro for complex operations
- **Retry Logic**: Built-in retry mechanism with exponential backoff
- **Centralized AI Client**: Single AI client instance shared across all agents with configuration management

### Error Handling and Reliability
- **Safe Execution Wrapper**: All agent operations wrapped in error handling with graceful degradation
- **Health Check System**: Continuous monitoring of agent and service health
- **Logging Framework**: Comprehensive logging across all components
- **Input Validation**: Standardized input validation for all agent operations

## External Dependencies

### AI Services
- **Google Gemini API**: Primary AI service for natural language processing, content generation, and analysis
- **API Key Management**: Environment variable-based configuration for secure API access

### Database Services
- **Supabase**: Primary cloud PostgreSQL database for production data storage
- **SQLite**: Local fallback database for offline operation and development

### Integration Services
- **Slack API**: Optional integration for team notifications and workflow updates
- **Notion API**: Optional integration for project documentation and knowledge management
- **Jira API**: Optional integration for task management and project tracking

### Development Dependencies
- **Streamlit**: Web application framework for the user interface
- **SQLAlchemy**: Database ORM for cross-database compatibility
- **Pandas**: Data manipulation and analysis for metrics and reporting
- **Plotly**: Interactive visualization for dashboards and analytics
- **Asyncio**: Asynchronous programming support for concurrent operations

### Configuration Management
- **Environment Variables**: All sensitive configuration managed through environment variables
- **Centralized Config**: Single configuration class managing all service settings
- **Flexible Integration**: Optional external service integrations with graceful degradation