'use client';

import { useRouter } from 'next/navigation';
import { Dna, Shield, Lock, Trash2, Eye, Server, UserCheck, ChevronRight, CheckCircle } from 'lucide-react';

export default function PrivacyPage() {
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
              <button onClick={() => router.push('/how-it-works')} className="hover:text-ng-lime transition-colors">How It Works</button>
              <span className="text-ng-lime cursor-default">Privacy</span>
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
      <section className="bg-ng-dark py-14">
        <div className="container mx-auto px-4 max-w-4xl text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-ng-dark-2 mb-6 border border-ng-dark-3">
            <Shield className="w-8 h-8 text-ng-lime" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-4">
            Privacy <span className="text-ng-lime">Policy</span>
          </h1>
          <p className="text-base text-[#A0B8A0] font-medium max-w-2xl mx-auto">
            Your genetic data is among the most sensitive personal information that exists. Here is exactly how we handle it — with transparency and respect.
          </p>
          <p className="mt-3 text-sm text-[#708070] font-medium">Last updated: March 2026</p>
        </div>
      </section>

      {/* Summary Badges */}
      <section className="py-12 bg-ng-light border-b border-ng-border">
        <div className="container mx-auto px-4 max-w-5xl">
          <div className="flex flex-wrap justify-center gap-4">
            {[
              { icon: <Lock className="w-4 h-4 text-ng-lime" />, text: 'End-to-end encrypted' },
              { icon: <Trash2 className="w-4 h-4 text-ng-lime" />, text: 'DNA files deleted after analysis' },
              { icon: <Eye className="w-4 h-4 text-ng-lime" />, text: 'Never sold to third parties' },
              { icon: <UserCheck className="w-4 h-4 text-ng-lime" />, text: 'GDPR compliant' },
              { icon: <Trash2 className="w-4 h-4 text-ng-lime" />, text: 'Delete your account anytime' },
            ].map(({ icon, text }) => (
              <div key={text} className="flex items-center gap-2 bg-ng-dark px-5 py-2.5 rounded-lg border border-ng-dark-3">
                {icon}
                <span className="text-white text-sm font-semibold">{text}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Content */}
      <section className="py-16">
        <div className="container mx-auto px-4 max-w-3xl">
          <div className="space-y-12">

            {/* Section 1 */}
            <PolicySection
              icon={<Server className="w-6 h-6 text-ng-dark" />}
              title="What Data We Collect"
            >
              <p>When you use GenyO, we collect the following categories of information:</p>
              <ul className="space-y-3 mt-4">
                {[
                  { label: 'Account data', detail: 'Your name, email address, age, and sex — provided during registration.' },
                  { label: 'Genetic data', detail: 'The raw DNA file you upload (from 23andMe, AncestryDNA, or similar providers). This file is processed immediately and then permanently deleted from disk.' },
                  { label: 'Derived genetic findings', detail: 'Structured results extracted from your genetic file (e.g., specific SNP variants and associated risk levels). These are encrypted and stored in our database to power your report.' },
                  { label: 'Lifestyle questionnaire answers', detail: 'Optional responses you provide about diet, exercise, and health goals, used to personalise your nutrition plan.' },
                  { label: 'Usage data', detail: 'Basic server logs (IP address, request timestamps) retained for up to 30 days for security purposes only.' },
                ].map(({ label, detail }) => (
                  <li key={label} className="flex items-start gap-3">
                    <div className="w-1.5 h-1.5 rounded-full bg-ng-lime flex-shrink-0 mt-2" />
                    <span className="text-ng-text-2 font-medium text-sm"><strong className="text-ng-text">{label}:</strong> {detail}</span>
                  </li>
                ))}
              </ul>
            </PolicySection>

            {/* Section 2 */}
            <PolicySection
              icon={<Lock className="w-6 h-6 text-ng-dark" />}
              title="How We Protect Your Data"
            >
              <p>We apply multiple layers of security to keep your information safe:</p>
              <div className="grid sm:grid-cols-2 gap-4 mt-5">
                {[
                  { title: 'Fernet Encryption at Rest', desc: 'All genetic findings stored in our database are encrypted using symmetric Fernet encryption. The encryption key is never stored alongside the data.' },
                  { title: 'TLS in Transit', desc: 'All communication between your browser and our servers is encrypted via HTTPS/TLS. Your raw DNA file never travels over an unencrypted connection.' },
                  { title: 'Immediate File Deletion', desc: 'Raw genome files are deleted from disk immediately after analysis completes. We do not archive or back up the original file — only the derived findings.' },
                  { title: 'No Plain-Text Storage', desc: 'Passwords are hashed with bcrypt before storage. No plain-text credentials are ever written to disk or logs.' },
                ].map(({ title, desc }) => (
                  <div key={title} className="bg-ng-light rounded-xl p-5 border border-ng-border">
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle className="w-4 h-4 text-ng-lime flex-shrink-0" />
                      <p className="font-bold text-ng-text text-sm">{title}</p>
                    </div>
                    <p className="text-xs text-ng-muted font-medium leading-relaxed">{desc}</p>
                  </div>
                ))}
              </div>
            </PolicySection>

            {/* Section 3 */}
            <PolicySection
              icon={<Eye className="w-6 h-6 text-ng-dark" />}
              title="How We Use Your Data"
            >
              <p>We use your data exclusively to provide and improve GenyO. Specifically:</p>
              <ul className="space-y-3 mt-4">
                {[
                  'To generate your personalised nutrigenomics report and nutrition recommendations.',
                  'To save your reports so you can access them later from your account.',
                  'To send you verification and account management emails (you can opt out at any time).',
                  'To maintain the security and integrity of the platform (fraud prevention, abuse detection).',
                  'To improve our analysis algorithms using aggregated, anonymised, never individually identifiable statistics.',
                ].map((item) => (
                  <li key={item} className="flex items-start gap-3">
                    <div className="w-5 h-5 rounded-full bg-ng-lime flex items-center justify-center flex-shrink-0 mt-0.5">
                      <CheckCircle className="w-3 h-3 text-ng-dark" />
                    </div>
                    <span className="text-ng-text-2 font-medium text-sm">{item}</span>
                  </li>
                ))}
              </ul>
              <div className="mt-6 p-4 bg-ng-dark rounded-xl border border-ng-dark-3">
                <p className="text-white font-semibold text-sm">We will never:</p>
                <ul className="mt-2 space-y-1.5 text-sm text-[#A0B8A0] font-medium">
                  <li>• Sell, rent, or share your genetic data with any third party</li>
                  <li>• Use your data for advertising or profiling purposes</li>
                  <li>• Provide your data to insurance companies, employers, or governments</li>
                  <li>• Share your data with pharmaceutical or biotech companies</li>
                </ul>
              </div>
            </PolicySection>

            {/* Section 4 */}
            <PolicySection
              icon={<UserCheck className="w-6 h-6 text-ng-dark" />}
              title="Your Rights (GDPR)"
            >
              <p>If you are in the European Union or European Economic Area, you have the following rights under the GDPR:</p>
              <div className="mt-5 space-y-3">
                {[
                  { right: 'Right of Access', detail: 'You can request a copy of all personal data we hold about you at any time.' },
                  { right: 'Right to Rectification', detail: 'You can update your name, age, and sex directly from your Profile page. Contact us for other corrections.' },
                  { right: 'Right to Erasure ("Right to be Forgotten")', detail: 'You can delete your entire account and all associated data from your Profile settings. Deletion is permanent and irreversible.' },
                  { right: 'Right to Data Portability', detail: 'You can request a machine-readable export of your genetic findings and profile data.' },
                  { right: 'Right to Restrict Processing', detail: 'You can contact us to request that we stop processing your data while a dispute is pending.' },
                  { right: 'Right to Object', detail: 'You can object to processing based on legitimate interest, including for statistical analysis purposes.' },
                ].map(({ right, detail }) => (
                  <div key={right} className="flex items-start gap-3 p-4 bg-white rounded-xl border border-ng-border">
                    <div className="w-1.5 h-1.5 rounded-full bg-ng-lime flex-shrink-0 mt-2" />
                    <div>
                      <p className="font-bold text-ng-text text-sm">{right}</p>
                      <p className="text-ng-muted text-sm font-medium mt-0.5">{detail}</p>
                    </div>
                  </div>
                ))}
              </div>
              <p className="mt-5 text-ng-text-2 font-medium text-sm">
                To exercise any of these rights, email us at <span className="font-bold text-ng-dark">privacy@gen.myo.sh</span>. We will respond within 30 days.
              </p>
            </PolicySection>

            {/* Section 5 */}
            <PolicySection
              icon={<Trash2 className="w-6 h-6 text-ng-dark" />}
              title="Data Retention"
            >
              <p>We keep your data only as long as necessary:</p>
              <div className="mt-5 overflow-hidden rounded-xl border border-ng-border">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-ng-dark text-white">
                      <th className="text-left px-4 py-3 font-semibold">Data Type</th>
                      <th className="text-left px-4 py-3 font-semibold">Retention Period</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-ng-border">
                    {[
                      ['Raw DNA file', 'Deleted immediately after analysis'],
                      ['Derived genetic findings', 'Until you delete your account'],
                      ['Account profile (name, email, age, sex)', 'Until you delete your account'],
                      ['Analysis reports', 'Until you delete the report or your account'],
                      ['Server access logs', '30 days'],
                      ['Verification codes', '15 minutes (auto-expired)'],
                    ].map(([type, retention]) => (
                      <tr key={type} className="bg-white even:bg-ng-light">
                        <td className="px-4 py-3 text-ng-text font-medium">{type}</td>
                        <td className="px-4 py-3 text-ng-muted font-medium">{retention}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </PolicySection>

            {/* Section 6 */}
            <PolicySection
              icon={<Server className="w-6 h-6 text-ng-dark" />}
              title="Third-Party Services"
            >
              <p>GenyO uses a limited number of third-party services, each bound by strict data processing agreements:</p>
              <ul className="space-y-3 mt-4">
                {[
                  { name: 'Groq / LLaMA', purpose: 'AI-generated meal plan text. We send only anonymised nutrition parameters — no personal identifiers or genetic data.' },
                  { name: 'MongoDB Atlas (or self-hosted)', purpose: 'Encrypted database storage for account data and genetic findings. If hosted on Atlas, data resides in EU-West regions.' },
                  { name: 'SMTP email provider (Gmail)', purpose: 'Sending account verification and transactional emails. No genetic data is ever transmitted via email.' },
                ].map(({ name, purpose }) => (
                  <li key={name} className="flex items-start gap-3 p-4 bg-white rounded-xl border border-ng-border">
                    <div className="w-1.5 h-1.5 rounded-full bg-ng-lime flex-shrink-0 mt-2" />
                    <div>
                      <p className="font-bold text-ng-text text-sm">{name}</p>
                      <p className="text-ng-muted text-sm font-medium mt-0.5">{purpose}</p>
                    </div>
                  </li>
                ))}
              </ul>
              <p className="mt-4 text-ng-text-2 font-medium text-sm">
                We do not use any advertising networks, analytics trackers, or social media pixels.
              </p>
            </PolicySection>

            {/* Section 7 */}
            <PolicySection
              icon={<Shield className="w-6 h-6 text-ng-dark" />}
              title="Children's Privacy"
            >
              <p className="text-ng-text-2 font-medium text-sm leading-relaxed">
                GenyO is not intended for individuals under the age of 18. We do not knowingly collect personal data from minors. If you believe a minor has created an account, please contact us immediately at <span className="font-bold text-ng-dark">privacy@gen.myo.sh</span> and we will delete the account within 48 hours.
              </p>
            </PolicySection>

            {/* Section 8 */}
            <PolicySection
              icon={<Shield className="w-6 h-6 text-ng-dark" />}
              title="Changes to This Policy"
            >
              <p className="text-ng-text-2 font-medium text-sm leading-relaxed">
                We may update this Privacy Policy from time to time. When we do, we will update the "Last updated" date at the top of this page and, for material changes, notify you by email. Continued use of GenyO after changes take effect constitutes acceptance of the updated policy.
              </p>
            </PolicySection>

            {/* Contact */}
            <div className="bg-ng-dark rounded-2xl p-8 text-center">
              <Shield className="w-10 h-10 text-ng-lime mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-white mb-3">Questions About Your Privacy?</h2>
              <p className="text-[#A0B8A0] font-medium mb-5 max-w-lg mx-auto">
                If you have any questions, concerns, or requests regarding your personal data, please reach out to our privacy team.
              </p>
              <a
                href="mailto:privacy@gen.myo.sh"
                className="inline-flex items-center gap-2 px-6 py-3 bg-ng-lime text-ng-text font-semibold rounded-lg hover:bg-[#b8d960] transition-colors"
              >
                privacy@gen.myo.sh
              </a>
            </div>

          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-ng-light border-t border-ng-border">
        <div className="container mx-auto px-4 max-w-3xl text-center">
          <h2 className="text-3xl font-bold text-ng-text mb-4">Ready to Analyze Your DNA?</h2>
          <p className="text-ng-text-2 font-medium mb-8">Your privacy is protected every step of the way.</p>
          <button
            onClick={() => router.push('/landing')}
            className="btn btn-primary text-base px-10 py-4 flex items-center gap-2 mx-auto"
          >
            Get Started
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

function PolicySection({ icon, title, children }: { icon: React.ReactNode; title: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="flex items-center gap-3 mb-5">
        <div className="w-11 h-11 rounded-xl bg-ng-lime flex items-center justify-center flex-shrink-0">
          {icon}
        </div>
        <h2 className="text-2xl font-bold text-ng-text">{title}</h2>
      </div>
      <div className="text-ng-text-2 font-medium leading-relaxed text-sm">
        {children}
      </div>
    </div>
  );
}
