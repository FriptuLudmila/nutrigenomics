'use client';

import { useState } from 'react';
import { Dna, Shield, TrendingUp, Zap, ChevronRight, CheckCircle } from 'lucide-react';
import AuthModal from '@/components/AuthModal';

export default function LandingPage() {
  const [showAuthModal, setShowAuthModal] = useState(false);

  return (
    <>
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
        {/* Navigation */}
        <nav className="bg-white border-b border-slate-200">
          <div className="container mx-auto px-4 py-4 max-w-7xl flex justify-between items-center">
            <div className="flex items-center gap-2">
              <Dna className="w-8 h-8 text-blue-600" />
              <span className="text-xl font-bold text-slate-900">NutriGenome</span>
            </div>
            <button
              onClick={() => setShowAuthModal(true)}
              className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700"
            >
              Sign In
            </button>
          </div>
        </nav>

        {/* Hero Section */}
        <section className="container mx-auto px-4 py-20 max-w-6xl">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-slate-900 mb-6">
              Your DNA Knows What
              <br />
              <span className="text-blue-600">You Should Eat</span>
            </h1>
            <p className="text-xl text-slate-600 mb-8 max-w-2xl mx-auto">
              Get personalized nutrition recommendations based on your genetic makeup.
              Upload your 23andMe or AncestryDNA data and discover the foods that work best for you.
            </p>
            <button
              onClick={() => setShowAuthModal(true)}
              className="btn btn-primary text-lg px-8 py-4 flex items-center gap-2 mx-auto"
            >
              Analyze My Data
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>

          {/* Hero Image Placeholder */}
          <div className="mt-16 relative">
            <div
              className="rounded-lg border-2 border-slate-200 bg-white shadow-xl overflow-hidden"
              style={{ height: '400px' }}
            >
              <div
                className="absolute inset-0 opacity-10"
                style={{
                  backgroundImage: 'url(/genes.png)',
                  backgroundRepeat: 'repeat',
                  backgroundSize: 'auto 50%',
                  backgroundPosition: 'center'
                }}
              />
              <div className="relative z-10 flex items-center justify-center h-full">
                <div className="text-center">
                  <Dna className="w-24 h-24 text-blue-600 mx-auto mb-4" />
                  <p className="text-slate-500 text-lg">Personalized Nutrigenomics Report Preview</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="bg-white py-20 border-t border-slate-200">
          <div className="container mx-auto px-4 max-w-6xl">
            <h2 className="text-3xl font-bold text-center text-slate-900 mb-12">
              How It Works
            </h2>
            <div className="grid md:grid-cols-3 gap-8">
              <FeatureCard
                icon={<Dna className="w-12 h-12 text-blue-600" />}
                title="Upload Your Data"
                description="Securely upload your genetic data from 23andMe, AncestryDNA, or other providers. Your data is encrypted and GDPR compliant."
              />
              <FeatureCard
                icon={<Zap className="w-12 h-12 text-blue-600" />}
                title="AI Analysis"
                description="Our advanced algorithm analyzes 25+ genetic variants related to nutrition, metabolism, and dietary sensitivities."
              />
              <FeatureCard
                icon={<TrendingUp className="w-12 h-12 text-blue-600" />}
                title="Get Recommendations"
                description="Receive personalized meal plans, supplement suggestions, and dietary advice tailored to your unique genetic profile."
              />
            </div>
          </div>
        </section>

        {/* Benefits Section */}
        <section className="py-20">
          <div className="container mx-auto px-4 max-w-6xl">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="text-3xl font-bold text-slate-900 mb-6">
                  Discover What Makes You Unique
                </h2>
                <p className="text-slate-600 mb-6">
                  Everyone's body processes nutrients differently. Your genetic variants influence how you
                  metabolize vitamins, respond to caffeine, digest dairy, and much more.
                </p>
                <ul className="space-y-3">
                  <BenefitItem text="Vitamin & mineral absorption insights" />
                  <BenefitItem text="Food sensitivity detection (lactose, gluten, caffeine)" />
                  <BenefitItem text="Personalized macronutrient recommendations" />
                  <BenefitItem text="AI-generated meal plans based on your genetics" />
                  <BenefitItem text="Supplement suggestions tailored to your needs" />
                </ul>
              </div>
              <div className="bg-slate-100 rounded-lg p-8">
                <h3 className="text-xl font-semibold text-slate-900 mb-4">
                  Analyzed Genetic Markers Include:
                </h3>
                <div className="grid grid-cols-2 gap-3 text-sm text-slate-700">
                  <div>• Lactose tolerance</div>
                  <div>• Caffeine metabolism</div>
                  <div>• Vitamin D receptor</div>
                  <div>• Folate processing</div>
                  <div>• Omega-3 conversion</div>
                  <div>• Iron absorption</div>
                  <div>• Celiac risk</div>
                  <div>• Alcohol metabolism</div>
                  <div>• Vitamin B12 absorption</div>
                  <div>• Carb sensitivity</div>
                  <div>• Fat metabolism</div>
                  <div>• And 14 more...</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Privacy Section */}
        <section className="bg-blue-50 py-20 border-t border-blue-100">
          <div className="container mx-auto px-4 max-w-4xl text-center">
            <Shield className="w-16 h-16 text-blue-600 mx-auto mb-6" />
            <h2 className="text-3xl font-bold text-slate-900 mb-4">
              Your Privacy is Our Priority
            </h2>
            <p className="text-slate-700 mb-6">
              Your genetic data is encrypted end-to-end and never shared with third parties.
              We are GDPR compliant and you can delete your data at any time.
            </p>
            <div className="flex justify-center gap-8 text-sm text-slate-600">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span>Encrypted Storage</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span>GDPR Compliant</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span>No Third-Party Sharing</span>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20">
          <div className="container mx-auto px-4 max-w-4xl text-center">
            <h2 className="text-4xl font-bold text-slate-900 mb-6">
              Ready to Unlock Your Genetic Potential?
            </h2>
            <p className="text-xl text-slate-600 mb-8">
              Start your personalized nutrition journey today
            </p>
            <button
              onClick={() => setShowAuthModal(true)}
              className="btn btn-primary text-lg px-8 py-4 flex items-center gap-2 mx-auto"
            >
              Get Started Now
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </section>

        {/* Footer */}
        <footer className="bg-slate-900 text-white py-12">
          <div className="container mx-auto px-4 max-w-6xl">
            <div className="grid md:grid-cols-3 gap-8 mb-8">
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <Dna className="w-6 h-6" />
                  <span className="font-bold">NutriGenome</span>
                </div>
                <p className="text-slate-400 text-sm">
                  Personalized nutrition based on your genetics
                </p>
              </div>
              <div>
                <h4 className="font-semibold mb-3">Product</h4>
                <ul className="space-y-2 text-sm text-slate-400">
                  <li>How it works</li>
                  <li>Genetic markers</li>
                  <li>Pricing</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold mb-3">Legal</h4>
                <ul className="space-y-2 text-sm text-slate-400">
                  <li>Privacy Policy</li>
                  <li>Terms of Service</li>
                  <li>GDPR Compliance</li>
                </ul>
              </div>
            </div>
            <div className="border-t border-slate-800 pt-8 text-center text-sm text-slate-400">
              <p>Medical Disclaimer: This analysis is for educational purposes only. Always consult healthcare professionals before making dietary changes.</p>
              <p className="mt-4">© 2024 NutriGenome. All rights reserved.</p>
            </div>
          </div>
        </footer>
      </div>

      {/* Auth Modal */}
      <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
    </>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="text-center">
      <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-blue-50 mb-4">
        {icon}
      </div>
      <h3 className="text-xl font-semibold text-slate-900 mb-3">{title}</h3>
      <p className="text-slate-600">{description}</p>
    </div>
  );
}

function BenefitItem({ text }: { text: string }) {
  return (
    <li className="flex items-start gap-2">
      <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
      <span className="text-slate-700">{text}</span>
    </li>
  );
}
