import { useState } from 'react'

export default function CodeBlock({ code, lang = '' }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="code-block group">
      {lang && (
        <div className="px-4 pt-3 text-xs text-zinc-500 font-mono">{lang}</div>
      )}
      <pre><code>{code}</code></pre>
      <button
        onClick={handleCopy}
        className={`copy-btn ${copied ? 'copied' : 'opacity-0 group-hover:opacity-100'}`}
      >
        {copied ? '已复制' : '复制'}
      </button>
    </div>
  )
}
