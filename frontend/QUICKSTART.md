# Frontend Quick Start

## Prerequisites
- Flask backend running on http://localhost:5000
- Node.js 18+ installed

## Installation & Run

```bash
# 1. Install dependencies (first time only)
npm install

# 2. Start development server
npm run dev
```

Open http://localhost:3000

## That's it! 🎉

The app will guide you through:
1. Upload genetic file
2. Auto-analysis
3. Questionnaire
4. View personalized recommendations

## Build for Production

```bash
npm run build
npm start
```

## Environment Variables

Create `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:5000
```

Already created for you!
