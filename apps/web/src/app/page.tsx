export default function Home() {
  return <main className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6 py-16">
    <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal-800">Teknologji · piloto de saúde pública</p>
    <h1 className="mt-4 max-w-3xl text-4xl font-semibold leading-tight md:text-6xl">AI Oral Scan</h1>
    <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-600">Triagem odontológica escolar, continuidade do cuidado e inteligência territorial em uma plataforma segura.</p>
    <section className="mt-12 grid gap-4 md:grid-cols-3" aria-label="Princípios do piloto">
      {[['Decisão clínica humana', 'O cirurgião-dentista valida achados, prioridades e encaminhamentos.'], ['Dados protegidos', 'Desenvolvimento com dados sintéticos e informações agregadas para gestão.'], ['Operação de campo', 'App Android offline e painel web compartilhando uma API versionada.']].map(([title, body]) => <article key={title} className="rounded-2xl border border-teal-900/10 bg-white p-6 shadow-sm"><h2 className="font-semibold">{title}</h2><p className="mt-2 text-sm leading-6 text-slate-600">{body}</p></article>)}
    </section>
    <p className="mt-10 text-sm text-slate-500">Fundação do produto · análise clínica por IA desativada</p>
  </main>;
}
