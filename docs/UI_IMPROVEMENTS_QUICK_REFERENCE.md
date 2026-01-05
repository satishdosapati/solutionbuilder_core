# 🚀 UI Improvements Quick Reference Guide

Quick implementation examples for common improvements.

---

## 1. Install Dependencies

```bash
cd frontend
npm install framer-motion lucide-react prismjs @types/prismjs
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-tooltip
npm install clsx tailwind-merge
```

---

## 2. Enhanced Mode Selector with Framer Motion

**Before**: Basic gradient buttons  
**After**: Animated with smooth transitions

```typescript
import { motion } from 'framer-motion';
import { Brain, Search, Zap } from 'lucide-react';

const ModeSelector = ({ currentMode, onModeChange }) => {
  const modes = [
    { key: 'brainstorm', label: 'Brainstorm', icon: Brain, color: 'orange' },
    { key: 'analyze', label: 'Analyze', icon: Search, color: 'blue' },
    { key: 'generate', label: 'Generate', icon: Zap, color: 'green' }
  ];

  return (
    <div className="inline-flex items-center gap-1 p-1 bg-gray-100 dark:bg-gray-800 rounded-xl">
      {modes.map((mode) => (
        <motion.button
          key={mode.key}
          onClick={() => onModeChange(mode.key)}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className={`relative px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
            currentMode === mode.key
              ? `bg-gradient-to-r from-${mode.color}-500 to-${mode.color}-600 text-white`
              : 'text-gray-600 dark:text-gray-400'
          }`}
        >
          {currentMode === mode.key && (
            <motion.div
              layoutId="activeMode"
              className="absolute inset-0 bg-gradient-to-r rounded-lg"
              initial={false}
              transition={{ type: "spring", stiffness: 500, damping: 30 }}
            />
          )}
          <span className="relative flex items-center gap-1.5">
            <mode.icon className="w-4 h-4" />
            <span>{mode.label}</span>
          </span>
        </motion.button>
      ))}
    </div>
  );
};
```

---

## 3. Animated Message List

**Before**: Static message rendering  
**After**: Staggered entrance animations

```typescript
import { motion, AnimatePresence } from 'framer-motion';

const ChatInterface = ({ messages }) => {
  return (
    <div className="flex-1 overflow-y-auto">
      <AnimatePresence initial={false}>
        {messages.map((message, index) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ 
              duration: 0.3,
              delay: index * 0.05 // Stagger effect
            }}
          >
            <MessageBubble message={message} />
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};
```

---

## 4. Enhanced Code Block with Prism.js

**Before**: Plain code display  
**After**: Syntax highlighting with copy button

```typescript
import { useEffect, useRef } from 'react';
import Prism from 'prismjs';
import 'prismjs/themes/prism-tomorrow.css';
import { Copy, Check } from 'lucide-react';

const CodeBlock = ({ code, language }) => {
  const codeRef = useRef(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (codeRef.current) {
      Prism.highlightElement(codeRef.current);
    }
  }, [code, language]);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative group">
      <div className="flex items-center justify-between bg-gray-800 px-4 py-2 rounded-t-lg">
        <span className="text-xs text-gray-400 uppercase">{language}</span>
        <motion.button
          onClick={handleCopy}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          className="flex items-center gap-2 text-xs text-gray-400 hover:text-white"
        >
          {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
          {copied ? 'Copied!' : 'Copy'}
        </motion.button>
      </div>
      <pre className="bg-gray-900 rounded-b-lg overflow-auto">
        <code ref={codeRef} className={`language-${language}`}>
          {code}
        </code>
      </pre>
    </div>
  );
};
```

---

## 5. Loading Skeleton Component

**Before**: Basic spinner  
**After**: Skeleton loader matching content structure

```typescript
import { motion } from 'framer-motion';

const MessageSkeleton = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex gap-3 p-4"
    >
      <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 animate-pulse" />
      <div className="flex-1 space-y-2">
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 animate-pulse" />
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 animate-pulse" />
      </div>
    </motion.div>
  );
};
```

---

## 6. Enhanced Button with Micro-interactions

**Before**: Basic button  
**After**: Animated with hover/tap effects

```typescript
import { motion } from 'framer-motion';
import { Send } from 'lucide-react';

const SendButton = ({ onClick, disabled, isLoading }) => {
  return (
    <motion.button
      onClick={onClick}
      disabled={disabled || isLoading}
      whileHover={{ scale: disabled ? 1 : 1.05 }}
      whileTap={{ scale: disabled ? 1 : 0.95 }}
      className={`
        px-5 py-3 rounded-xl font-semibold
        bg-gradient-to-r from-blue-600 to-blue-500
        text-white shadow-lg
        disabled:opacity-50 disabled:cursor-not-allowed
      `}
    >
      {isLoading ? (
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        >
          <Loader className="w-5 h-5" />
        </motion.div>
      ) : (
        <div className="flex items-center gap-2">
          <Send className="w-5 h-5" />
          <span>Send</span>
        </div>
      )}
    </motion.button>
  );
};
```

---

## 7. Toast Notification System

**Before**: No feedback for actions  
**After**: Toast notifications for success/error

```typescript
import * as Toast from '@radix-ui/react-toast';
import { motion, AnimatePresence } from 'framer-motion';

const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const showToast = (message, type = 'info') => {
    const id = Date.now();
    setToasts([...toasts, { id, message, type }]);
    setTimeout(() => {
      setToasts(toasts.filter(t => t.id !== id));
    }, 3000);
  };

  return (
    <Toast.Provider>
      {children}
      <AnimatePresence>
        {toasts.map((toast) => (
          <motion.div
            key={toast.id}
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed top-4 right-4 bg-white dark:bg-gray-800 p-4 rounded-lg shadow-lg"
          >
            {toast.message}
          </motion.div>
        ))}
      </AnimatePresence>
    </Toast.Provider>
  );
};
```

---

## 8. Improved Input with Character Count

**Before**: Basic textarea  
**After**: Enhanced with animations and feedback

```typescript
import { motion } from 'framer-motion';

const EnhancedInput = ({ value, onChange, placeholder, maxLength }) => {
  const [focused, setFocused] = useState(false);
  const remaining = maxLength - value.length;

  return (
    <motion.div
      animate={{
        scale: focused ? 1.01 : 1,
        boxShadow: focused 
          ? '0 0 0 3px rgba(59, 130, 246, 0.1)' 
          : '0 0 0 0px rgba(59, 130, 246, 0.1)'
      }}
      className="relative"
    >
      <textarea
        value={value}
        onChange={onChange}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        placeholder={placeholder}
        maxLength={maxLength}
        className="w-full rounded-xl px-4 py-3 border-2 border-gray-200 dark:border-gray-700 focus:border-blue-500"
      />
      {maxLength && (
        <motion.div
          animate={{ opacity: focused || value.length > 0 ? 1 : 0 }}
          className="absolute bottom-2 right-2 text-xs text-gray-400"
        >
          {remaining} remaining
        </motion.div>
      )}
    </motion.div>
  );
};
```

---

## 9. Accessibility Improvements

### Add ARIA Labels
```typescript
<button
  aria-label="Switch to brainstorm mode"
  aria-pressed={currentMode === 'brainstorm'}
  onClick={() => onModeChange('brainstorm')}
>
  Brainstorm
</button>
```

### Keyboard Navigation
```typescript
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'ArrowRight' && currentMode !== 'generate') {
    const modes = ['brainstorm', 'analyze', 'generate'];
    const nextIndex = modes.indexOf(currentMode) + 1;
    onModeChange(modes[nextIndex]);
  }
  if (e.key === 'ArrowLeft' && currentMode !== 'brainstorm') {
    const modes = ['brainstorm', 'analyze', 'generate'];
    const prevIndex = modes.indexOf(currentMode) - 1;
    onModeChange(modes[prevIndex]);
  }
};
```

### Focus Indicators
```css
/* Add to index.css */
*:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}
```

---

## 10. Tailwind Config Enhancements

```javascript
// tailwind.config.js
export default {
  theme: {
    extend: {
      // Add animation utilities
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      // Add transition utilities
      transitionDuration: {
        '400': '400ms',
        '600': '600ms',
      },
      // Add spacing scale
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
    },
  },
}
```

---

## 🎯 Quick Wins (Implement First)

1. **Replace emojis with Lucide icons** (15 min)
2. **Add Framer Motion to ModeSelector** (30 min)
3. **Add message entrance animations** (30 min)
4. **Install Prism.js for code blocks** (45 min)
5. **Add loading skeletons** (30 min)

**Total Time**: ~2.5 hours for significant visual improvements

---

## 📚 Additional Resources

- [Framer Motion Examples](https://www.framer.com/motion/examples/)
- [shadcn/ui Components](https://ui.shadcn.com/docs/components)
- [Lucide Icons](https://lucide.dev/icons)
- [Prism.js Themes](https://prismjs.com/download.html#themes=prism-tomorrow)

