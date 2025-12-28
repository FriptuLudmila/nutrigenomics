# Nutrigenomics Frontend

A modern, user-friendly web interface for the Nutrigenomics Analysis platform built with Next.js, TypeScript, and Tailwind CSS.

## Features

- 🧬 **File Upload**: Drag-and-drop interface for genetic data files (23andMe, AncestryDNA)
- 📋 **Lifestyle Questionnaire**: Comprehensive form to gather lifestyle and health information
- 📊 **Personalized Reports**: Beautiful, easy-to-read recommendations based on 25+ genetic variants
- 🎨 **Modern UI**: Clean, responsive design with Tailwind CSS
- 🔒 **Privacy-Focused**: Secure communication with encrypted backend

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- The Flask backend running on `http://localhost:5000`

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file (already created):
```
NEXT_PUBLIC_API_URL=http://localhost:5000
```

4. Run the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
frontend/
├── app/
│   ├── globals.css          # Global styles with Tailwind
│   ├── layout.tsx            # Root layout
│   └── page.tsx              # Main application page
├── components/
│   ├── FileUpload.tsx        # File upload component with drag-and-drop
│   ├── Questionnaire.tsx     # Lifestyle questionnaire form
│   └── RecommendationsReport.tsx  # Results display component
├── lib/
│   └── api.ts                # API client for backend communication
├── public/                   # Static assets
└── package.json              # Dependencies and scripts
```

## Usage Flow

1. **Upload**: User uploads their genetic data file
2. **Analysis**: Backend automatically analyzes the genetic variants
3. **Questionnaire**: User fills out lifestyle questions
4. **Results**: Personalized recommendations are generated and displayed

## API Integration

The frontend communicates with the Flask backend via REST API:

- `POST /api/upload` - Upload genetic file
- `POST /api/analyze` - Analyze genetics
- `POST /api/questionnaire` - Submit lifestyle answers
- `GET /api/recommendations/:sessionId` - Get personalized recommendations

## Building for Production

```bash
npm run build
npm start
```

## Technologies Used

- **Next.js 15** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **React Hooks** - State management

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## License

Educational project - see main repository for details
