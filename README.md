# Smart Job Application Tracker

An intelligent job application tracking system that automatically monitors your email for job-related communications and extracts application details using AI. Built with FastAPI backend and React frontend.

## Features

- 🤖 **AI-Powered Email Analysis** - Automatically detects and extracts job application details from emails
- 📧 **Email Monitoring** - Real-time IMAP monitoring of your inbox for job-related emails
- 📊 **Statistics Dashboard** - Comprehensive analytics on your job application activity
- 🔄 **Real-time Updates** - WebSocket integration for live data synchronization
- 🎯 **Application Management** - Track applications with status updates and filtering
- ⚡ **Quick Actions** - Easy controls for monitoring and data management

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **OpenAI API** - Email content analysis and job detail extraction
- **WebSockets** - Real-time communication
- **IMAP** - Email monitoring
- **SQLite** - Database storage

### Frontend
- **React 19** - Modern UI framework
- **TypeScript** - Type-safe development
- **Redux Toolkit** - State management
- **Tailwind CSS** - Utility-first styling
- **Vite** - Fast build tool
- **Lucide React** - Icon library

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Email account with IMAP access (Gmail recommended)
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd job_application_tracker
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp env_template.txt .env
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Configure Environment**
   
   Edit `backend/.env` with your credentials:
   ```env
   EMAIL_ADDRESS=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   OPENAI_API_KEY=your_openai_api_key
   ```

   For Gmail users, see [Email Setup Guide](backend/README_EMAIL_SETUP.md) for app password configuration.

### Running the Application

1. **Start Backend** (Terminal 1)
   ```bash
   cd backend
   python main.py
   ```

2. **Start Frontend** (Terminal 2)
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## How It Works

1. **Email Monitoring** - The system connects to your email via IMAP and monitors for new messages
2. **AI Analysis** - When job-related emails are detected, OpenAI analyzes the content to extract:
   - Company name
   - Position title
   - Application status
   - Job posting URLs
   - Contact information
3. **Data Storage** - Extracted information is stored in SQLite database
4. **Real-time Updates** - WebSocket connections keep the frontend synchronized with new data
5. **Dashboard Analytics** - View comprehensive statistics and manage applications through the web interface

## Project Structure

```
job_application_tracker/
├── backend/
│   ├── api/routes/          # API endpoints
│   ├── agent/               # Email monitoring and processing
│   ├── config/              # Application configuration
│   ├── database/            # Database models and management
│   ├── services/            # WebSocket and other services
│   ├── utils/               # Utility functions
│   └── main.py              # Application entry point
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # API client services
│   │   ├── store/           # Redux store and slices
│   │   └── types/           # TypeScript type definitions
│   └── package.json
└── README.md
```

## API Endpoints

- `GET /api/applications/` - List all job applications
- `GET /api/statistics/` - Get application statistics
- `POST /api/monitor/start` - Start email monitoring
- `POST /api/monitor/stop` - Stop email monitoring
- `GET /api/monitor/status` - Get monitoring status
- `WebSocket /ws` - Real-time updates

## Development

### Backend Development

```bash
cd backend
# Install dependencies
pip install -r requirements.txt

# Run with hot reload
uvicorn main:app --reload

# Run tests (if available)
pytest
```

### Frontend Development

```bash
cd frontend
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `EMAIL_ADDRESS` | Your email address for monitoring | Required |
| `EMAIL_PASSWORD` | Email password or app password | Required |
| `OPENAI_API_KEY` | OpenAI API key for email analysis | Required |
| `DATABASE_URL` | Database connection string | `sqlite:///./database.db` |
| `API_HOST` | Backend host address | `127.0.0.1` |
| `API_PORT` | Backend port number | `8000` |
| `EMAIL_CHECK_INTERVAL` | Email check frequency (seconds) | `300` |
| `DEBUG` | Enable debug logging | `true` |

## Security Notes

- Never commit `.env` files to version control
- Use app passwords instead of your main email password
- Keep your OpenAI API key secure
- The application stores data locally in SQLite by default

## Troubleshooting

### Email Connection Issues
- Verify email credentials in `.env` file
- For Gmail, ensure 2FA is enabled and use app password
- Check if "Less secure app access" needs to be enabled

### Frontend Build Issues
- Ensure Node.js version is 18+
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check for TypeScript errors: `npm run build`

### Backend Issues
- Verify Python version is 3.11+
- Check all required environment variables are set
- Review logs for specific error messages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is private and intended for personal use.