'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Dna, Shield, TrendingUp, Zap, ChevronRight, CheckCircle } from 'lucide-react';
import AuthModal from '@/components/AuthModal';

export default function LandingPage() {
  const router = useRouter();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
    setIsLoggedIn(!!token);
  }, []);

  return (
    <>
      <div className="min-h-screen bg-ng-cream">
        {/* Announcement Bar */}
        <div className="bg-ng-dark-2 border-b border-ng-dark-3">
          <div className="container mx-auto px-4 py-3 max-w-7xl">
            <div className="flex justify-center items-center gap-2 px-5 py-3 bg-ng-dark-3 rounded-md text-sm font-medium text-white">
              <Dna className="w-4 h-4 text-ng-lime flex-shrink-0" />
              <span>Analyze your 23andMe or AncestryDNA data — personalized nutrition for free</span>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="bg-ng-dark border-b border-ng-dark-2">
          <div className="container mx-auto px-4 py-5 max-w-7xl flex justify-between items-center">
            <button onClick={() => router.push('/landing')} className="flex items-center gap-2 hover:opacity-80 transition-opacity">
              <Dna className="w-8 h-8 text-ng-lime" />
              <span className="text-xl font-bold text-white">GenyO</span>
            </button>
            <div className="flex items-center gap-8">
              <div className="hidden md:flex items-center gap-6 text-ng-cream text-base font-semibold">
                <span className="text-ng-lime cursor-default">Home</span>
                <button onClick={() => router.push('/how-it-works')} className="hover:text-ng-lime transition-colors">How It Works</button>
                <button onClick={() => router.push('/privacy')} className="hover:text-ng-lime transition-colors">Privacy</button>
              </div>
              <button
                onClick={() => isLoggedIn ? router.push('/app') : setShowAuthModal(true)}
                className="px-6 py-3 bg-ng-lime text-ng-text font-semibold rounded-lg hover:bg-[#b8d960] transition-colors"
              >
                {isLoggedIn ? 'Go to App' : 'Get Started'}
              </button>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <section className="flex items-stretch min-h-[420px]">
          {/* Left: image placeholder */}
          <div className="hidden md:block w-[55%] flex-shrink-0 rounded-br-[50px] overflow-hidden">
            <img
              src="/Gemini_Generated_Image_h4sio9h4sio9h4si.png"
              alt="Personalized nutrition"
              className="w-full h-full object-cover min-h-[420px]"
            />
          </div>

          {/* Right: content */}
          <div className="flex-1 flex items-center px-10 md:px-16 py-12">
            <div className="max-w-xl">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-ng-light border border-ng-border rounded-full text-sm font-medium text-ng-text-2 mb-8">
                <Dna className="w-4 h-4 text-ng-dark" />
                Precision nutrition powered by your genetics
              </div>
              <h1 className="text-5xl md:text-6xl font-bold text-ng-text mb-6">
                Your DNA Knows What
                <br />
                <span className="text-ng-dark">You Should Eat</span>
              </h1>
              <p className="text-lg text-ng-text-2 mb-10 font-medium">
                Get personalized nutrition recommendations based on your genetic makeup.
                Upload your 23andMe or AncestryDNA data and discover the foods that work best for you.
              </p>
              <div className="flex flex-col sm:flex-row items-start gap-4">
                <button
                  onClick={() => isLoggedIn ? router.push('/app') : setShowAuthModal(true)}
                  className="btn btn-primary text-base px-8 py-4 flex items-center gap-2"
                >
                  {isLoggedIn ? 'Go to App' : 'Analyze My Data'}
                  <ChevronRight className="w-5 h-5" />
                </button>
                {!isLoggedIn && (
                  <button
                    onClick={() => setShowAuthModal(true)}
                    className="px-8 py-4 text-base font-semibold text-ng-dark bg-ng-light border border-ng-border rounded-lg hover:bg-ng-border transition-colors"
                  >
                    Sign In
                  </button>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section className="bg-ng-light border-t border-b border-ng-border py-24">
          <div className="container mx-auto px-4 max-w-6xl">
            <div className="text-center mb-14">
              <h2 className="text-4xl font-bold text-ng-text mb-4">How It Works</h2>
              <p className="text-ng-text-2 max-w-xl mx-auto font-medium">Three simple steps to unlock your genetic nutrition profile</p>
            </div>
            <div className="grid md:grid-cols-3 gap-8">
              <FeatureCard
                icon={<Dna className="w-8 h-8 text-ng-dark" />}
                title="Upload Your Data"
                description="Securely upload your genetic data from 23andMe, AncestryDNA, or other providers. Your data is encrypted and GDPR compliant."
              />
              <FeatureCard
                icon={<Zap className="w-8 h-8 text-ng-dark" />}
                title="AI Analysis"
                description="Our advanced algorithm analyzes 25+ genetic variants related to nutrition, metabolism, and dietary sensitivities."
              />
              <FeatureCard
                icon={<TrendingUp className="w-8 h-8 text-ng-dark" />}
                title="Get Recommendations"
                description="Receive personalized meal plans, supplement suggestions, and dietary advice tailored to your unique genetic profile."
              />
            </div>
          </div>
        </section>

        {/* Benefits Section */}
        <section className="py-24">
          <div className="container mx-auto px-4 max-w-6xl">
            <div className="grid md:grid-cols-2 gap-16 items-center">
              <div>
                <h2 className="text-4xl font-bold text-ng-text mb-6">
                  Discover What Makes You Unique
                </h2>
                <p className="text-ng-text-2 mb-8 font-medium">
                  Everyone&apos;s body processes nutrients differently. Your genetic variants influence how you
                  metabolize vitamins, respond to caffeine, digest dairy, and much more.
                </p>
                <ul className="space-y-4">
                  <BenefitItem text="Vitamin & mineral absorption insights" />
                  <BenefitItem text="Food sensitivity detection (lactose, gluten, caffeine)" />
                  <BenefitItem text="Personalized macronutrient recommendations" />
                  <BenefitItem text="AI-generated meal plans based on your genetics" />
                  <BenefitItem text="Supplement suggestions tailored to your needs" />
                </ul>
              </div>
              <div className="bg-ng-light rounded-2xl p-8 border border-ng-border">
                <h3 className="text-xl font-semibold text-ng-text mb-6">
                  Analyzed Genetic Markers Include:
                </h3>
                <div className="grid grid-cols-2 gap-3 text-sm text-ng-text-2 font-medium">
                  {[
                    'Lactose tolerance', 'Caffeine metabolism',
                    'Vitamin D receptor', 'Folate processing',
                    'Omega-3 conversion', 'Iron absorption',
                    'Celiac risk', 'Alcohol metabolism',
                    'Vitamin B12 absorption', 'Carb sensitivity',
                    'Fat metabolism', 'And 14 more...'
                  ].map((item) => (
                    <div key={item} className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-ng-lime flex-shrink-0" />
                      {item}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Privacy Section */}
        <section className="bg-ng-dark py-24">
          <div className="container mx-auto px-4 max-w-4xl text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-ng-dark-2 mb-8 border border-ng-dark-3">
              <Shield className="w-10 h-10 text-ng-lime" />
            </div>
            <h2 className="text-4xl font-bold text-white mb-5">
              Your Privacy is Our Priority
            </h2>
            <p className="text-[#E6E6E6] mb-10 text-lg font-medium max-w-2xl mx-auto">
              Your genetic data is encrypted end-to-end and never shared with third parties.
              We are GDPR compliant and you can delete your data at any time.
            </p>
            <div className="flex flex-wrap justify-center gap-6">
              <div className="flex items-center gap-3 bg-ng-dark-2 px-5 py-3 rounded-lg border border-ng-dark-3">
                <CheckCircle className="w-5 h-5 text-ng-lime" />
                <span className="text-white font-semibold">Encrypted Storage</span>
              </div>
              <div className="flex items-center gap-3 bg-ng-dark-2 px-5 py-3 rounded-lg border border-ng-dark-3">
                <CheckCircle className="w-5 h-5 text-ng-lime" />
                <span className="text-white font-semibold">GDPR Compliant</span>
              </div>
              <div className="flex items-center gap-3 bg-ng-dark-2 px-5 py-3 rounded-lg border border-ng-dark-3">
                <CheckCircle className="w-5 h-5 text-ng-lime" />
                <span className="text-white font-semibold">No Third-Party Sharing</span>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-24 bg-ng-light border-t border-ng-border">
          <div className="container mx-auto px-4 max-w-4xl text-center">
            <h2 className="text-4xl font-bold text-ng-text mb-5">
              Ready to Unlock Your Genetic Potential?
            </h2>
            <p className="text-lg text-ng-text-2 mb-10 font-medium">
              Start your personalized nutrition journey today
            </p>
            <button
              onClick={() => isLoggedIn ? router.push('/app') : setShowAuthModal(true)}
              className="btn btn-primary text-base px-10 py-4 flex items-center gap-2 mx-auto"
            >
              {isLoggedIn ? 'Go to App' : 'Get Started Now'}
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </section>

        {/* Footer */}
        <footer className="bg-ng-dark text-white py-14 border-t border-ng-dark-2">
          <div className="container mx-auto px-4 max-w-6xl">
            <div className="grid md:grid-cols-3 gap-10 mb-10">
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <Dna className="w-6 h-6 text-ng-lime" />
                  <span className="font-bold text-lg">GenyO</span>
                </div>
                <p className="text-[#A0A0A0] text-sm font-medium">
                  Personalized nutrition based on your genetics
                </p>
              </div>
              <div>
                <h4 className="font-semibold mb-4 text-ng-lime">Product</h4>
                <ul className="space-y-2 text-sm text-[#A0A0A0] font-medium">
                  <li>How it works</li>
                  <li>Genetic markers</li>
                  <li>Pricing</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold mb-4 text-ng-lime">Legal</h4>
                <ul className="space-y-2 text-sm text-[#A0A0A0] font-medium">
                  <li>Privacy Policy</li>
                  <li>Terms of Service</li>
                  <li>GDPR Compliance</li>
                </ul>
              </div>
            </div>
            <div className="border-t border-ng-dark-2 pt-8 text-center text-sm text-[#A0A0A0] font-medium">
              <p>Medical Disclaimer: This analysis is for educational purposes only. Always consult healthcare professionals before making dietary changes.</p>
              <p className="mt-3">© 2024 GenyO. All rights reserved.</p>
            </div>
          </div>
        </footer>
      </div>

      <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
    </>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="bg-white rounded-2xl p-8 border border-ng-border hover:shadow-md transition-shadow">
      <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-ng-lime mb-5">
        {icon}
      </div>
      <h3 className="text-xl font-semibold text-ng-text mb-3">{title}</h3>
      <p className="text-ng-text-2 font-medium">{description}</p>
    </div>
  );
}

function BenefitItem({ text }: { text: string }) {
  return (
    <li className="flex items-start gap-3">
      <div className="w-5 h-5 rounded-full bg-ng-lime flex items-center justify-center flex-shrink-0 mt-0.5">
        <CheckCircle className="w-3 h-3 text-ng-dark" />
      </div>
      <span className="text-ng-text-2 font-medium">{text}</span>
    </li>
  );
}
