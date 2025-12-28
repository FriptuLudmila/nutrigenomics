# Nutrigenomics Platform - Complete Setup Guide

A full-stack nutrigenomics analysis platform with Flask backend and Next.js frontend.

## 🎯 What This Does

Upload your genetic data (23andMe, AncestryDNA) and get personalized nutrition recommendations based on 25+ genetic variants affecting:
- Vitamin metabolism (B12, D, folate, etc.)
- Food sensitivities (lactose, gluten, caffeine, alcohol)
- Macronutrient processing (carbs, fats, omega-3)
- Weight management
- Detoxification
- And more!

## 📋 Prerequisites

### Required Software
- **Python 3.8+** (for backend)
- **Node.js 18+** and npm (for frontend)
- **MongoDB** (running on localhost:27017)

### Check if MongoDB is running:
```bash
# Windows
tasklist | findstr mongod

# Mac/Linux
ps aux | grep mongod
```

If not running, start MongoDB or install from https://www.mongodb.com/try/download/community

## 🚀 Quick Start

### Backend Setup (Flask API)

1. **Navigate to project root:**
```bash
cd nutrigenomics
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Verify `.env` file exists with encryption key:**
```bash
cat .env
```

Should contain:
```
FLASK_DEBUG=True
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=nutrigenomics
ENCRYPTION_KEY=BC51wPT1j_YTOzeqU3yJkfZBM3hSt4E6LzZ2v-l0CP0=
```

4. **Start the Flask server:**
```bash
python run.py
```

Server should start at http://localhost:5000

### Frontend Setup (Next.js)

1. **Open a NEW terminal and navigate to frontend:**
```bash
cd nutrigenomics/frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Verify `.env.local` exists:**
```bash
cat .env.local
```

Should contain:
```
NEXT_PUBLIC_API_URL=http://localhost:5000
```

4. **Start the development server:**
```bash
npm run dev
```

Frontend should start at http://localhost:3000

## 🧪 Testing the Application

### Option 1: Use the Web Interface

1. Open http://localhost:3000 in your browser
2. Upload your genetic file (genome_Joshua_Yoakem_v5_Full_20250129211749.txt or similar)
3. Wait for analysis
4. Fill out the questionnaire
5. View your personalized recommendations!

### Option 2: Use the Test Script

```bash
# Make sure Flask server is running first!
python test_api.py genome_Joshua_Yoakem_v5_Full_20250129211749.txt
```

## 📁 Project Structure

```
nutrigenomics/
├── app/                      # Flask backend
│   ├── __init__.py          # App factory
│   ├── routes.py            # API endpoints
│   ├── database.py          # MongoDB connection
│   ├── models.py            # Data models
│   ├── genetic_parser.py    # SNP analysis
│   ├── encryption.py        # Data encryption
│   └── config.py            # Configuration
├── frontend/                # Next.js frontend
│   ├── app/                 # Next.js pages
│   │   ├── page.tsx         # Main app page
│   │   ├── layout.tsx       # Root layout
│   │   └── globals.css      # Global styles
│   ├── components/          # React components
│   │   ├── FileUpload.tsx
│   │   ├── Questionnaire.tsx
│   │   └── RecommendationsReport.tsx
│   ├── lib/
│   │   └── api.ts           # API client
│   └── package.json
├── uploads/                 # Uploaded genetic files
├── run.py                   # Backend entry point
├── test_api.py              # API test script
├── .env                     # Environment variables
└── requirements.txt         # Python dependencies
```

## 🔧 API Endpoints

All endpoints are prefixed with `/api`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload genetic file |
| POST | `/api/analyze` | Analyze uploaded genetics |
| GET | `/api/questionnaire/template` | Get questionnaire structure |
| POST | `/api/questionnaire` | Submit lifestyle answers |
| GET | `/api/recommendations/:id` | Get personalized recommendations |
| GET | `/api/session/:id` | Check session status |
| DELETE | `/api/session/:id` | Delete all session data (GDPR) |
| GET | `/api/snps` | List all analyzed SNPs |

## 🧬 Supported Genetic Variants (25 SNPs)

### Digestive & Taste
- rs4988235 - Lactose intolerance
- rs2187668 - Celiac disease risk
- rs1726866 - Bitter taste perception
- rs1761667 - Fat taste perception

### Caffeine & Alcohol
- rs762551 - Caffeine metabolism (CYP1A2)
- rs671 - Alcohol flush reaction (ALDH2)
- rs1229984 - Alcohol metabolism (ADH1B)

### Vitamins
- rs1801133 - MTHFR C677T (folate)
- rs1801131 - MTHFR A1298C (folate)
- rs602662 - Vitamin B12 absorption
- rs1801394 - Vitamin B12 utilization
- rs2228570 - Vitamin D receptor
- rs7041 - Vitamin D transport
- rs33972313 - Vitamin C
- rs7501331 - Beta-carotene conversion
- rs7946 - Choline needs

### Macronutrients & Weight
- rs174546 - Omega-3 conversion (FADS1)
- rs5082 - Saturated fat sensitivity
- rs7903146 - Carb metabolism/diabetes risk (TCF7L2)
- rs9939609 - Obesity risk (FTO)

### Minerals & Antioxidants
- rs1799945 - Iron absorption
- rs4880 - Antioxidant (SOD2)
- rs1695 - Detoxification (GSTP1)

### Other
- rs4341 - Exercise response (ACE)

## 🔐 Security Features

- **Encryption**: Genetic data encrypted with Fernet (AES-128)
- **Session Management**: UUID-based sessions
- **GDPR Compliance**: Delete endpoint to remove all user data
- **Secure Storage**: MongoDB with encrypted sensitive fields

## 🐛 Troubleshooting

### Backend Issues

**"Database error" when uploading:**
- Make sure MongoDB is running
- Check that `.env` has the ENCRYPTION_KEY set

**"Module not found" errors:**
```bash
pip install -r requirements.txt
```

**"Address already in use" (port 5000):**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :5000
kill -9 <PID>
```

### Frontend Issues

**"Cannot connect to API":**
- Make sure Flask server is running on port 5000
- Check `.env.local` has correct API URL

**npm install errors:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Port 3000 in use:**
```bash
# Next.js will automatically use 3001 if 3000 is taken
# Or kill the process using port 3000
```

## 📊 Database Collections

MongoDB stores data in 4 collections:

1. **sessions** - User sessions and file metadata
2. **genetic_results** - Encrypted genetic findings
3. **questionnaires** - Lifestyle answers
4. **recommendations** - Generated recommendations

View data:
```bash
mongosh
use nutrigenomics
db.sessions.find().pretty()
```

## 🎨 Customization

### Adding New SNPs

Edit `app/genetic_parser.py`:
1. Add SNP to `NUTRIGENOMICS_SNPS` dictionary
2. Update recommendation logic in `app/routes.py` `generate_personalized_recommendations()`

### Styling

Frontend uses Tailwind CSS. Modify:
- `frontend/app/globals.css` - Global styles
- Component files - Individual component styles

## 📝 Development Tips

### Backend Development
```bash
# Flask auto-reloads with debug=True
python run.py
```

### Frontend Development
```bash
# Next.js has hot reload
cd frontend
npm run dev
```

### View Logs
- Backend: Terminal running `python run.py`
- Frontend: Terminal running `npm run dev` + browser console

## 🚢 Production Deployment

### Backend
```bash
# Set production environment variables
export FLASK_DEBUG=False
export SECRET_KEY=<strong-secret-key>
export ENCRYPTION_KEY=<your-encryption-key>

# Use production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Frontend
```bash
cd frontend
npm run build
npm start
```

## 📄 License

Educational project for Bachelor thesis.

## 🆘 Support

For issues or questions:
1. Check this guide first
2. Review error messages in terminal
3. Check MongoDB is running
4. Verify all dependencies are installed

---

**Ready to start?** Follow the Quick Start section above! 🚀
