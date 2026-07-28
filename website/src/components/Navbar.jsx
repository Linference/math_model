import { useState } from 'react'

const links = [
  { label: '功能', href: '#features' },
  { label: '对比', href: '#comparison' },
  { label: '流程', href: '#workflow' },
  { label: '安装', href: '#setup' },
  { label: '下载', href: '#download' },
]

export default function Navbar() {
  const [open, setOpen] = useState(false)

  return (
    <nav className="fixed top-0 w-full z-50 border-b border-zinc-800/80 bg-zinc-950/80 backdrop-blur-md">
      <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
        <a href="#" className="text-sm font-semibold text-zinc-200 tracking-tight">
          Math Modeling Skill
        </a>

        <div className="hidden md:flex items-center gap-8">
          {links.map(l => (
            <a key={l.href} href={l.href} className="text-sm text-zinc-400 hover:text-zinc-100 transition-colors">
              {l.label}
            </a>
          ))}
          <a href="#download" className="text-sm px-4 py-1.5 rounded-md bg-zinc-100 text-zinc-900 font-medium hover:bg-zinc-200 transition-colors">
            下载 v2.0
          </a>
        </div>

        <button className="md:hidden text-zinc-400" onClick={() => setOpen(!open)}>
          {open ? '关闭' : '菜单'}
        </button>
      </div>

      {open && (
        <div className="md:hidden border-t border-zinc-800 bg-zinc-950 px-6 py-4 flex flex-col gap-3">
          {links.map(l => (
            <a key={l.href} href={l.href} onClick={() => setOpen(false)} className="text-sm text-zinc-400">
              {l.label}
            </a>
          ))}
          <a href="#download" className="text-sm text-center px-4 py-2 rounded-md bg-zinc-100 text-zinc-900 font-medium">
            下载 v2.0
          </a>
        </div>
      )}
    </nav>
  )
}
