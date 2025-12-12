import { Link } from "wouter";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white m-5">
      {/* Top gradient background like reference */}
      <div className="absolute inset-x-0 top-0 h-[520px] -z-10 [background:radial-gradient(600px_500px_at_90%_8%,#ffd4bd_0%,transparent_60%),radial-gradient(500px_360px_at_12%_24%,#e8eeff_0%,transparent_60%),linear-gradient(180deg,#fff8f3,transparent_60%)]" />
      <header className="sticky top-0 z-20 bg-white/70 backdrop-blur border-b border-black/5">
        <div className="mx-auto max-w-6xl px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 font-extrabold tracking-tight">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-emerald-500" />
            <span>GrowIQ</span>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm text-slate-600">
            <a href="#why" className="hover:text-slate-900">Top Collabs</a>
            <a href="#story" className="hover:text-slate-900">Inside Story</a>
            <a href="#contact" className="hover:text-slate-900">Let's Talk</a>
          </nav>
          <div className="flex items-center gap-2">
            <Link href="/login" className="px-3 py-2 rounded-lg border border-slate-200 font-semibold">Log In</Link>
            <Link href="/signup" className="px-3 py-2 rounded-lg bg-gradient-to-tr from-indigo-600 to-violet-500 text-white font-semibold">Begin Journey</Link>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4">
        {/* Hero */}
        <section className="grid md:grid-cols-2 gap-6 items-center pt-10 pb-2 pl-6 md:pl-14">
          <div>
            <h1 className="text-4xl md:text-6xl font-extrabold leading-tight">
              Your <span className="text-emerald-500">Next</span> Career Move
              <br /> Starts Here.
            </h1>
            <p className="mt-4 text-slate-600 max-w-xl">
              Discover people, companies, and opportunities tailored for your
              industry. Build your presence. Make meaningful connections.
            </p>
            <div className="mt-6 flex items-center gap-3">
              <Link href="/signup" className="px-4 py-2 rounded-full bg-[#6C5CE7] text-white font-semibold shadow-sm">Get Started</Link>
              <Link href="/login" className="px-4 py-2 rounded-full border border-slate-200 font-semibold">Log In</Link>
            </div>
            <div className="mt-6 flex items-center gap-6 opacity-70">
              {['wipro','accenture','tcs','hcl','siemens','oracle'].map((n) => (
                <img key={n} src={`/figmaAssets/frame.svg`} alt={n} className="h-6" />
              ))}
            </div>
          </div>
          <div className="relative aspect-square rounded-3xl border border-slate-200 overflow-hidden bg-gradient-to-br from-rose-50 via-indigo-50 to-emerald-50">
            <img
              src="/static/landing/hero.png"
              alt="Landing visual"
              className="absolute right-6 bottom-6 w-1/2 rounded-xl shadow-xl hidden md:block"
              onError={(e) => ((e.currentTarget.style.display = "none"))}
            />
          </div>
        </section>

        {/* Feature cards row like reference */}
        <section className="mt-6 grid md:grid-cols-2 gap-4">
          <div className="rounded-2xl border border-indigo-200 bg-white p-4 shadow-[0_10px_30px_rgba(17,12,46,0.04)]">
            <div className="text-[13px] font-semibold">New Month, New Opportunities, Stay Ahead with Fresh Listings!</div>
            <div className="text-slate-600 text-xs mt-1">Every month brings new openings — be the first to discover what's next.</div>
          </div>
          <div className="rounded-2xl border border-indigo-200 bg-white p-4 shadow-[0_10px_30px_rgba(17,12,46,0.04)]">
            <div className="text-[13px] font-semibold">Real Jobs. Real HR Reach outs. Guaranteed.</div>
            <div className="text-slate-600 text-xs mt-1">Genuine roles, verified recruiters — no gimmicks, just results.</div>
          </div>
        </section>

        {/* Decorative wave band */}
        <section className="relative mt-8">
          <svg viewBox="0 0 1440 200" className="w-full h-[140px]" preserveAspectRatio="none">
            <defs>
              <linearGradient id="lg" x1="0" x2="1" y1="0" y2="0">
                <stop offset="0%" stopColor="#8B5CF6" stopOpacity="0.5" />
                <stop offset="50%" stopColor="#22D3EE" stopOpacity="0.5" />
                <stop offset="100%" stopColor="#10B981" stopOpacity="0.5" />
              </linearGradient>
            </defs>
            <path d="M0,120 C240,30 480,210 720,120 C960,30 1200,210 1440,120 L1440,200 L0,200 Z" fill="url(#lg)" />
          </svg>
        </section>

        {/* Why GrowIQ */}
        <section id="why" className="py-6">
          <div className="grid md:grid-cols-2 gap-4">
            <div className="rounded-2xl border-2 border-indigo-200/70 p-4 bg-white/70 shadow-sm">
              <h3 className="font-semibold">New Month, New Opportunities, Stay Ahead with Fresh Listings!</h3>
              <p className="text-slate-600 text-sm mt-1">Every month brings new openings — be the first to discover what's next.</p>
            </div>
            <div className="rounded-2xl border-2 border-indigo-200/70 p-4 bg-white/70 shadow-sm">
              <h3 className="font-semibold">Real Jobs. Real HR Reach outs. Guaranteed.</h3>
              <p className="text-slate-600 text-sm mt-1">Genuine roles, verified recruiters — no gimmicks, just results.</p>
            </div>
          </div>
        </section>

        {/* Feature band with wave (simplified) */}
        <section className="relative my-8">
          <div className="h-24 rounded-2xl bg-gradient-to-r from-indigo-200 via-sky-200 to-emerald-200" />
          <div className="absolute inset-x-0 -bottom-6 flex justify-between px-4">
            <button className="size-10 rounded-full bg-white shadow border">◀</button>
            <button className="size-10 rounded-full bg-white shadow border">▶</button>
          </div>
        </section>

        {/* AI Copy */}
        <section className="py-10 grid md:grid-cols-[1fr_1.3fr] gap-6 items-center">
          <div className="rounded-3xl overflow-hidden">
            <img
              src="/figmaAssets/th--8--1.png"
              alt="VR Kid"
              className="w-full h-full object-cover"
            />
          </div>
          <div>
            <h4 className="font-bold">AI-Powered Career Path. Precision. Speed. Success.</h4>
            <p className="text-slate-600 text-sm mt-2 leading-relaxed">
              Our advanced AI system analyzes your resume, background, and preferences to calculate a personalized profile score. Using this, we match you with the most relevant job opportunities.
            </p>
          </div>
        </section>

        {/* Numbers */}
        <section id="numbers" className="py-8">
          <p className="text-sky-700 font-semibold">Dice By The Number</p>
          <div className="grid md:grid-cols-3 gap-4 mt-4">
            {[
              {n:"5K+", d:"Companies hire on Dice"},
              {n:"200K+", d:"Jobs posted monthly on Dice"},
              {n:"7M+", d:"Tech professionals trust Dice"},
            ].map((s) => (
              <div key={s.n} className="rounded-2xl border border-slate-200 p-6 bg-white shadow-[0_10px_30px_rgba(17,12,46,0.04)]">
                <div className="text-3xl font-extrabold">{s.n}</div>
                <div className="text-slate-600 text-sm mt-1">{s.d}</div>
              </div>
            ))}
          </div>
        </section>

        {/* CTA Banner */}
        <section className="relative my-10 rounded-3xl border border-slate-200 overflow-hidden">
          <div className="p-6 md:p-10 bg-[radial-gradient(circle_at_20%_20%,#fde68a,transparent_40%),radial-gradient(circle_at_80%_20%,#e9d5ff,transparent_40%),radial-gradient(circle_at_80%_80%,#a7f3d0,transparent_40%),#ffffff]">
            <h5 className="text-center font-semibold text-sky-700">Where Your Career Takes Off – Tech or Core</h5>
            <p className="text-center text-slate-700 text-sm mt-2 max-w-2xl mx-auto">
              Join thousands of students landing jobs in both tech and core industries. Explore companies, apply to real roles, get expert advice — all in one place.
            </p>
            <div className="mt-4 flex justify-center">
              <Link href="/signup" className="px-4 py-2 rounded-full bg-[#6C5CE7] text-white font-semibold shadow-sm">Create Your Profile Now</Link>
            </div>
          </div>
          <img
            src="/figmaAssets/th--1--1.png"
            alt="Person with headphones"
            className="hidden md:block absolute right-4 bottom-0 w-56"
          />
        </section>
      </main>

      <footer className="py-10 text-center text-slate-600">
        <small>© {new Date().getFullYear()} GrowIQ. All rights reserved.</small>
      </footer>
    </div>
  );
}
