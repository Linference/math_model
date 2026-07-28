import { Link, useLocation, Outlet } from 'react-router-dom'
import { useState } from 'react'

const navLinks = [
  { to: '/', label: '首页' },
  { to: '/docs', label: '文档' },
  { to: '/changelog', label: '更新日志' },
  { to: '/thanks', label: '致谢' },
]

export default function Layout() {
  const { pathname } = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <div className="min-h-screen">
      {/* Nav */}
      <nav className="fixed top-0 w-full z-50 glass-nav">
        <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 text-sm font-semibold text-zinc-200 hover:text-white transition-colors">
            <span className="w-2 h-2 rounded-full bg-green-500" />
            MathModel Skill
          </Link>

          <div className="hidden md:flex items-center gap-1">
            {navLinks.map(l => (
              <Link
                key={l.to}
                to={l.to}
                className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
                  pathname === l.to
                    ? 'bg-white/10 text-zinc-100'
                    : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/5'
                }`}
              >
                {l.label}
              </Link>
            ))}
            <a
              href="https://github.com/Linference/math_model/releases/latest"
              target="_blank"
              rel="noopener noreferrer"
              className="ml-3 px-4 py-1.5 rounded-md bg-green-500 text-black text-sm font-medium hover:bg-green-400 transition-colors"
            >
              下载 v2.0
            </a>
          </div>

          <button className="md:hidden text-zinc-400 text-sm" onClick={() => setMenuOpen(!menuOpen)}>
            {menuOpen ? '关闭' : '菜单'}
          </button>
        </div>

        {menuOpen && (
          <div className="md:hidden glass border-t border-white/5 px-6 py-4 flex flex-col gap-1">
            {navLinks.map(l => (
              <Link
                key={l.to}
                to={l.to}
                onClick={() => setMenuOpen(false)}
                className={`px-3 py-2 rounded-md text-sm ${
                  pathname === l.to ? 'bg-white/10 text-zinc-100' : 'text-zinc-400'
                }`}
              >
                {l.label}
              </Link>
            ))}
          </div>
        )}
      </nav>

      {/* Content */}
      <main className="pt-14">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="border-t border-white/5 py-12 px-6">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-zinc-500">
          <div>
            MathModel Skill v2.0 —{' '}
            <a href="https://github.com/Linference/math_model" target="_blank" rel="noopener noreferrer" className="text-zinc-400 hover:text-zinc-200 transition-colors">
              GitHub
            </a>
          </div>
          <div className="flex items-center gap-6">
            <a href="https://github.com/Linference/math_model/blob/main/LICENSE" target="_blank" rel="noopener noreferrer" className="hover:text-zinc-300 transition-colors">MIT License</a>
            <a href="https://github.com/Linference/math_model/releases" target="_blank" rel="noopener noreferrer" className="hover:text-zinc-300 transition-colors">Releases</a>
            <Link to="/changelog" className="hover:text-zinc-300 transition-colors">更新日志</Link>
          </div>
        </div>
      </footer>
    </div>
  )
}
