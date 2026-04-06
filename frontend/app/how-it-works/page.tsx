'use client';

import { useRouter } from 'next/navigation';
import { Dna, Upload, Zap, TrendingUp, Shield, ChevronRight, CheckCircle, Lock, FileText, Brain, Salad } from 'lucide-react';

export default function HowItWorksPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-ng-cream">
      {/* Navigation */}
      <nav className="bg-ng-dark border-b border-ng-dark-2">
        <div className="container mx-auto px-4 py-5 max-w-7xl flex justify-between items-center">
          <button onClick={() => router.push('/landing')} className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <Dna className="w-8 h-8 text-ng-lime" />
            <span className="text-xl font-bold text-white">GenyO</span>
          </button>
          <div className="flex items-center gap-8">
            <div className="hidden md:flex items-center gap-6 text-ng-cream text-base font-semibold">
              <button onClick={() => router.push('/landing')} className="hover:text-ng-lime transition-colors">Home</button>
              <span className="text-ng-lime cursor-default">How It Works</span>
              <button onClick={() => router.push('/privacy')} className="hover:text-ng-lime transition-colors">Privacy</button>
            </div>
            <button
              onClick={() => router.push('/landing')}
              className="px-6 py-3 bg-ng-lime text-ng-text font-semibold rounded-lg hover:bg-[#b8d960] transition-colors"
            >
              Get Started
            </button>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="bg-[#1e3d30] py-14 relative overflow-hidden">
        <div className="container mx-auto px-4 max-w-4xl text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-ng-dark-2 border border-ng-dark-3 rounded-full text-sm font-medium text-ng-lime mb-8">
            <Zap className="w-4 h-4" />
            Simple. Accurate. Personalized.
          </div>
          <h1 className="text-5xl font-bold text-white mb-6">
            How <span className="text-ng-lime">GenyO</span> Works
          </h1>
          <p className="text-lg text-[#A0B8A0] font-medium max-w-2xl mx-auto">
            From uploading your raw genetic file to receiving a fully personalized nutrition plan — here's exactly what happens at every step.
          </p>
        </div>
      </section>

      {/* Steps Overview */}
      <section className="py-20 bg-ng-light border-b border-ng-border">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: '01', icon: <Upload className="w-7 h-7 text-ng-dark" />, title: 'Upload Your DNA File', desc: 'Securely upload your raw genetic data file from 23andMe or AncestryDNA.' },
              { step: '02', icon: <Brain className="w-7 h-7 text-ng-dark" />,  title: 'AI Genetic Analysis',  desc: 'Our engine scans 25+ clinically-relevant SNPs linked to nutrition and metabolism.' },
              { step: '03', icon: <Salad className="w-7 h-7 text-ng-dark" />, title: 'Get Your Plan',         desc: 'Receive personalized food, supplement, and meal plan recommendations.' },
            ].map(({ step, icon, title, desc }) => (
              <div key={step} className="bg-white rounded-2xl p-8 border border-ng-border text-center relative">
                <span className="absolute -top-4 left-8 px-3 py-1 bg-ng-dark text-ng-lime text-xs font-bold rounded-full">Step {step}</span>
                <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-ng-lime mb-5 mt-2">
                  {icon}
                </div>
                <h3 className="text-lg font-bold text-ng-text mb-3">{title}</h3>
                <p className="text-ng-muted font-medium text-sm">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Step 1 Detail */}
      <section className="py-24">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-ng-light border border-ng-border rounded-full text-xs font-bold text-ng-dark mb-6">
                Step 01
              </div>
              <h2 className="text-4xl font-bold text-ng-text mb-6">Upload Your DNA File</h2>
              <p className="text-ng-text-2 font-medium mb-8">
                GenyO works with raw DNA data files exported directly from consumer genetic testing services. Simply download your raw data file from your provider's website, then drag and drop it here.
              </p>
              <ul className="space-y-4">
                {[
                  'Supports 23andMe (v3, v4, v5) and AncestryDNA formats',
                  'Files are encrypted immediately on upload — never stored in plain text',
                  'Genome files are deleted from disk right after analysis (GDPR by design)',
                  'Maximum file size: 50 MB',
                ].map(item => (
                  <li key={item} className="flex items-start gap-3">
                    <div className="w-5 h-5 rounded-full bg-ng-lime flex items-center justify-center flex-shrink-0 mt-0.5">
                      <CheckCircle className="w-3 h-3 text-ng-dark" />
                    </div>
                    <span className="text-ng-text-2 font-medium text-sm">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-ng-light rounded-2xl p-8 border border-ng-border">
              <div className="flex flex-col items-center justify-center text-center py-10 border-2 border-dashed border-ng-border rounded-xl bg-white">
                <div className="w-16 h-16 rounded-2xl bg-ng-lime flex items-center justify-center mb-4">
                  <Upload className="w-8 h-8 text-ng-dark" />
                </div>
                <p className="font-semibold text-ng-text mb-1">Drag & drop your file here</p>
                <p className="text-sm text-ng-muted font-medium">Supports .txt and .csv from 23andMe / AncestryDNA</p>
              </div>
              <div className="mt-4 flex items-center gap-2 text-xs text-ng-muted font-medium">
                <Lock className="w-3.5 h-3.5 text-ng-dark flex-shrink-0" />
                Your file is encrypted before leaving your browser session
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Step 2 Detail */}
      <section className="py-24 bg-ng-light border-t border-b border-ng-border">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div className="bg-white rounded-2xl p-8 border border-ng-border order-2 md:order-1">
              <h3 className="text-base font-bold text-ng-text mb-5">SNPs Analyzed</h3>
              <div className="grid grid-cols-2 gap-3">
                {[
                  ['MTHFR', 'Folate metabolism'],
                  ['LCT', 'Lactose tolerance'],
                  ['CYP1A2', 'Caffeine metabolism'],
                  ['VDR', 'Vitamin D receptor'],
                  ['APOE', 'Fat metabolism'],
                  ['HFE', 'Iron absorption'],
                  ['FADS1', 'Omega-3 conversion'],
                  ['HLA-DQ', 'Celiac / gluten risk'],
                  ['TCN2', 'Vitamin B12 absorption'],
                  ['FTO', 'Carbohydrate sensitivity'],
                  ['ADH1B', 'Alcohol metabolism'],
                  ['+ 14 more', ''],
                ].map(([gene, label]) => (
                  <div key={gene} className="flex items-center gap-2 bg-ng-light rounded-lg px-3 py-2 border border-ng-border">
                    <div className="w-1.5 h-1.5 rounded-full bg-ng-lime flex-shrink-0" />
                    <div>
                      <p className="text-xs font-bold text-ng-text">{gene}</p>
                      {label && <p className="text-xs text-ng-muted">{label}</p>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="order-1 md:order-2">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-ng-dark border border-ng-dark-3 rounded-full text-xs font-bold text-ng-lime mb-6">
                Step 02
              </div>
              <h2 className="text-4xl font-bold text-ng-text mb-6">AI Genetic Analysis</h2>
              <p className="text-ng-text-2 font-medium mb-8">
                After upload, GenyO's analysis engine parses your raw SNP file and cross-references it against a curated database of 25+ nutrigenomics variants. Risk levels are assigned per finding based on peer-reviewed literature.
              </p>
              <ul className="space-y-4">
                {[
                  'Risk levels: High, Moderate, Low, and Protective',
                  'Each finding includes an interpretation and dietary recommendation',
                  'You then complete a short lifestyle questionnaire to personalize results further',
                  'Analysis typically completes in under 30 seconds',
                ].map(item => (
                  <li key={item} className="flex items-start gap-3">
                    <div className="w-5 h-5 rounded-full bg-ng-dark flex items-center justify-center flex-shrink-0 mt-0.5">
                      <CheckCircle className="w-3 h-3 text-ng-lime" />
                    </div>
                    <span className="text-ng-text-2 font-medium text-sm">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Step 3 Detail */}
      <section className="py-24">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-ng-light border border-ng-border rounded-full text-xs font-bold text-ng-dark mb-6">
                Step 03
              </div>
              <h2 className="text-4xl font-bold text-ng-text mb-6">Your Personalized Plan</h2>
              <p className="text-ng-text-2 font-medium mb-8">
                The final report combines your genetic findings with your lifestyle questionnaire to produce a fully personalized nutrition plan — including foods to increase, foods to limit, and supplements to consider.
              </p>
              <ul className="space-y-4">
                {[
                  'High-priority and moderate-priority dietary recommendations',
                  'Foods to increase and foods to limit, based on your genetics',
                  'Supplement suggestions tailored to your deficiency risks',
                  'AI-generated 3-day meal plan powered by Groq / LLaMA',
                  'Nutrient radar chart showing your risk profile at a glance',
                ].map(item => (
                  <li key={item} className="flex items-start gap-3">
                    <div className="w-5 h-5 rounded-full bg-ng-lime flex items-center justify-center flex-shrink-0 mt-0.5">
                      <CheckCircle className="w-3 h-3 text-ng-dark" />
                    </div>
                    <span className="text-ng-text-2 font-medium text-sm">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="grid grid-cols-2 gap-4">
              {[
                { icon: <FileText className="w-6 h-6 text-ng-dark" />, title: 'Full Report', desc: 'All genetic findings with risk levels and interpretations' },
                { icon: <TrendingUp className="w-6 h-6 text-ng-dark" />, title: 'Nutrient Radar', desc: 'Visual chart of your nutrition risk categories' },
                { icon: <Salad className="w-6 h-6 text-ng-dark" />, title: 'Meal Plan', desc: 'AI-generated 3-day meal plan based on your genetics' },
                { icon: <Shield className="w-6 h-6 text-ng-dark" />, title: 'Saved Securely', desc: 'Reports saved to your account for future reference' },
              ].map(({ icon, title, desc }) => (
                <div key={title} className="bg-ng-light rounded-xl p-5 border border-ng-border">
                  <div className="w-11 h-11 rounded-lg bg-ng-lime flex items-center justify-center mb-3">
                    {icon}
                  </div>
                  <p className="font-bold text-ng-text text-sm mb-1">{title}</p>
                  <p className="text-xs text-ng-muted font-medium">{desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Privacy Banner */}
      <section className="bg-ng-dark py-20">
        <div className="container mx-auto px-4 max-w-5xl">
          <div className="flex flex-col md:flex-row items-center gap-10">
            <div className="w-16 h-16 rounded-2xl bg-ng-dark-2 border border-ng-dark-3 flex items-center justify-center flex-shrink-0">
              <Shield className="w-8 h-8 text-ng-lime" />
            </div>
            <div className="flex-1 text-center md:text-left">
              <h2 className="text-2xl font-bold text-white mb-3">Your Data Never Leaves Your Control</h2>
              <p className="text-[#A0B8A0] font-medium">
                Genome files are deleted from disk immediately after analysis. Only encrypted, structured findings are stored in the database — never the raw file. You can delete your account and all data at any time.
              </p>
            </div>
            <div className="flex flex-col gap-3 text-sm text-white font-semibold flex-shrink-0">
              <div className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-ng-lime" /> Fernet encryption at rest</div>
              <div className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-ng-lime" /> GDPR compliant</div>
              <div className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-ng-lime" /> No third-party data sharing</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 bg-ng-light border-t border-ng-border">
        <div className="container mx-auto px-4 max-w-3xl text-center">
          <h2 className="text-4xl font-bold text-ng-text mb-5">Ready to Get Started?</h2>
          <p className="text-lg text-ng-text-2 font-medium mb-10">
            Create your free account and upload your genetic file in under a minute.
          </p>
          <button
            onClick={() => router.push('/landing')}
            className="btn btn-primary text-base px-10 py-4 flex items-center gap-2 mx-auto"
          >
            Analyze My DNA
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-ng-dark text-white py-10 border-t border-ng-dark-2">
        <div className="container mx-auto px-4 max-w-6xl flex flex-col md:flex-row justify-between items-center gap-4">
          <button onClick={() => router.push('/landing')} className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <Dna className="w-6 h-6 text-ng-lime" />
            <span className="font-bold">GenyO</span>
          </button>
          <p className="text-xs text-[#A0A0A0] font-medium text-center">
            Medical Disclaimer: This analysis is for educational purposes only. Always consult healthcare professionals before making dietary changes.
          </p>
          <p className="text-xs text-[#A0A0A0] font-medium">© 2024 GenyO. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
