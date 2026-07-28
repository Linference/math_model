export default function Footer() {
  return (
    <footer className="py-12 px-6 border-t border-zinc-800/50">
      <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="text-sm text-zinc-500">
          Math Modeling Skill v2.0 —{' '}
          <a
            href="https://github.com/Linference/math_model"
            target="_blank"
            rel="noopener noreferrer"
            className="text-zinc-400 hover:text-zinc-200 transition-colors"
          >
            GitHub
          </a>
        </div>

        <div className="flex items-center gap-6 text-sm">
          <a
            href="https://github.com/Linference/math_model/blob/main/LICENSE"
            target="_blank"
            rel="noopener noreferrer"
            className="text-zinc-500 hover:text-zinc-300 transition-colors"
          >
            MIT License
          </a>
          <a
            href="https://github.com/Linference/math_model/releases"
            target="_blank"
            rel="noopener noreferrer"
            className="text-zinc-500 hover:text-zinc-300 transition-colors"
          >
            Releases
          </a>
          <a
            href="https://github.com/Linference/math_model/blob/main/skill/CHANGELOG.md"
            target="_blank"
            rel="noopener noreferrer"
            className="text-zinc-500 hover:text-zinc-300 transition-colors"
          >
            Changelog
          </a>
        </div>
      </div>
    </footer>
  )
}
