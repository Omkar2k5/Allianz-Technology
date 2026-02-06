import { useEffect, useRef, useState } from 'react'
import { cn } from '@/lib/utils'

interface AnimatedNumberProps {
    value: number
    decimals?: number
    suffix?: string
    duration?: number
    className?: string
}

export function AnimatedNumber({
    value,
    decimals = 0,
    suffix = '',
    duration = 600,
    className = ''
}: AnimatedNumberProps) {
    const [displayValue, setDisplayValue] = useState(value)
    const [isAnimating, setIsAnimating] = useState(false)
    const prevValueRef = useRef(value)

    useEffect(() => {
        // Skip if value hasn't changed
        if (prevValueRef.current === value) return

        console.log(`AnimatedNumber: ${prevValueRef.current} -> ${value}`)

        setIsAnimating(true)
        const startValue = prevValueRef.current
        const endValue = value
        const startTime = Date.now()
        const difference = endValue - startValue

        const animate = () => {
            const currentTime = Date.now()
            const elapsed = currentTime - startTime
            const progress = Math.min(elapsed / duration, 1)

            // Easing function (ease-out-cubic for smoother feel)
            const easeProgress = 1 - Math.pow(1 - progress, 3)
            const currentValue = startValue + difference * easeProgress

            setDisplayValue(currentValue)

            if (progress < 1) {
                requestAnimationFrame(animate)
            } else {
                setDisplayValue(endValue)
                prevValueRef.current = endValue
                setIsAnimating(false)
            }
        }

        requestAnimationFrame(animate)
    }, [value, duration])

    const formattedValue = decimals > 0
        ? displayValue.toFixed(decimals)
        : Math.round(displayValue).toLocaleString()

    return (
        <span
            className={cn(
                'tabular-nums transition-all duration-300',
                isAnimating && 'text-primary scale-105',
                className
            )}
        >
            {formattedValue}
            {suffix && <span className="text-sm font-normal ml-1">{suffix}</span>}
        </span>
    )
}
