# Component Redesign Implementation Guide

## ✅ COMPLETED

### 1. FileUpload.tsx
**Changes Made:**
- ✅ Replaced SVG with Lucide `Upload` icon
- ✅ Changed to slate color scheme (slate-300, slate-900, etc.)
- ✅ Replaced checkmark emojis with `CheckCircle` icons
- ✅ Replaced security emoji with `Shield` icon
- ✅ Clean professional styling
- ✅ Used global `.btn` and `.btn-primary` classes

## 🔄 REMAINING UPDATES

### 2. Questionnaire.tsx - Professional Form Design

**Key Changes Needed:**
```tsx
// Update header
<h2 className="text-2xl font-semibold text-slate-900 mb-2">
  Lifestyle Assessment
</h2>
<p className="text-sm text-slate-600 mb-8">
  Complete this brief assessment to personalize your recommendations
</p>

// Update all inputs to use professional styling
className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm
           focus:ring-2 focus:ring-blue-500 focus:border-transparent
           bg-white text-slate-900"

// Update labels
className="block text-sm font-medium text-slate-700 mb-1.5"

// Update checkboxes to be cleaner
className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"

// Update submit button
className="w-full btn btn-primary py-3"
```

**Color replacements:**
- `gray-900` → `slate-900`
- `gray-700` → `slate-700`
- `gray-600` → `slate-600`
- `gray-300` → `slate-300`
- `blue-600` → Keep (primary color)

### 3. RecommendationsReport.tsx - Data Visualization

**Major Changes Needed:**

1. **Remove all emojis:**
   - 🔴 → Use `AlertCircle` icon with red color
   - 🟡 → Use `AlertTriangle` icon with orange color
   - ✅ → Use `CheckCircle` icon
   - 💊 → Use `Pill` icon
   - ⚠️ → Use `AlertTriangle` icon
   - 📄 → Use `FileText` icon
   - 💡 → Use `Lightbulb` icon

2. **Professional metric cards:**
```tsx
<div className="grid grid-cols-2 md:grid-cols-4 gap-4">
  <div className="bg-white border border-slate-200 rounded-lg p-4">
    <div className="flex items-center justify-between mb-2">
      <span className="text-xs font-medium text-slate-600">High Risk</span>
      <AlertCircle className="w-4 h-4 text-red-500" />
    </div>
    <div className="text-2xl font-bold text-slate-900">{high_risk}</div>
  </div>
  {/* Repeat for other metrics */}
</div>
```

3. **Clean recommendation cards:**
```tsx
<div className="bg-white border border-slate-200 rounded-lg p-6">
  <div className="flex items-start gap-4">
    <div className="flex-shrink-0">
      <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center">
        <AlertCircle className="w-5 h-5 text-red-600" />
      </div>
    </div>
    <div className="flex-1">
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-semibold text-slate-900">{category}</h4>
        <span className="text-xs px-2 py-1 bg-slate-100 text-slate-700 rounded-full">
          {genetic_basis}
        </span>
      </div>
      <p className="text-sm text-slate-600 mb-3">{recommendation}</p>
      {personalized_note && (
        <div className="bg-blue-50 border border-blue-200 rounded p-3 text-xs text-blue-900">
          <strong>Personalized:</strong> {personalized_note}
        </div>
      )}
    </div>
  </div>
</div>
```

4. **Professional buttons:**
```tsx
import { Printer, RotateCw } from 'lucide-react';

<div className="flex gap-3">
  <button onClick={() => window.print()} className="btn btn-primary">
    <Printer className="w-4 h-4" />
    Print Report
  </button>
  <button onClick={onReset} className="btn btn-secondary">
    <RotateCw className="w-4 h-4" />
    New Analysis
  </button>
</div>
```

5. **Add secondary button style to globals.css:**
```css
.btn-secondary {
  background: white;
  color: var(--color-neutral-700);
  border: 1px solid var(--color-neutral-300);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--color-neutral-50);
  border-color: var(--color-neutral-400);
}
```

## Icons to Import

```tsx
import {
  AlertCircle,      // High priority
  AlertTriangle,    // Moderate priority/warnings
  CheckCircle,      // Success/completed
  TrendingUp,       // Positive trends
  Pill,            // Supplements
  Lightbulb,       // Tips/insights
  FileText,        // Documents
  Printer,         // Print action
  RotateCw,        // Refresh/reset
  ChevronDown,     // Expandable sections
  Info,            // Information
  Shield           // Security/privacy
} from 'lucide-react';
```

## Complete Color Scheme Reference

### Primary Actions
- `bg-blue-600` / `text-blue-600` - Buttons, links, active states
- `border-blue-600` - Focus states, active borders

### Text
- `text-slate-900` - Headings, primary text
- `text-slate-700` - Labels
- `text-slate-600` - Body text, descriptions
- `text-slate-500` - Secondary text
- `text-slate-400` - Disabled text

### Borders & Backgrounds
- `border-slate-200` - Standard borders
- `border-slate-300` - Input borders
- `bg-slate-50` - Page background
- `bg-white` - Card backgrounds

### Status Colors (use sparingly!)
- `text-red-600` / `bg-red-50` - High priority/errors
- `text-orange-600` / `bg-orange-50` - Moderate priority/warnings
- `text-green-600` / `bg-green-50` - Success/positive
- `text-blue-600` / `bg-blue-50` - Info/notes

## Testing Checklist

After implementing all changes:

- [ ] No emojis visible anywhere
- [ ] All icons from lucide-react
- [ ] Consistent slate color scheme
- [ ] No gradients (solid backgrounds only)
- [ ] Professional typography
- [ ] Clean spacing and alignment
- [ ] Responsive on mobile
- [ ] Print styling works
- [ ] All buttons use global classes
- [ ] Form inputs have proper focus states

## Quick Find & Replace

In Questionnaire.tsx and RecommendationsReport.tsx:

```
Find: text-gray-900    Replace: text-slate-900
Find: text-gray-800    Replace: text-slate-800
Find: text-gray-700    Replace: text-slate-700
Find: text-gray-600    Replace: text-slate-600
Find: text-gray-500    Replace: text-slate-500
Find: border-gray-300  Replace: border-slate-300
Find: bg-gray-         Replace: bg-slate-
```

Remove all:
- Emoji characters (🔴🟡✅💊⚠️📄💡🧬 etc.)
- Gradient backgrounds (bg-gradient-to-*)
- Replace with appropriate Lucide icons
