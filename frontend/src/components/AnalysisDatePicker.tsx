import { useEffect, useRef, useState } from "react"
import { format, parseISO } from "date-fns"
import { DayPicker } from "react-day-picker"

import "react-day-picker/style.css"


type AnalysisDatePickerProps = {
    availableDates: string[]
    selectedDate: string
    onDateChange: (date: string) => void
}


function AnalysisDatePicker({
    availableDates,
    selectedDate,
    onDateChange,
}: AnalysisDatePickerProps) {
    const [isOpen, setIsOpen] =
        useState(false)

    const containerRef =
        useRef<HTMLDivElement>(null)

    const selected = selectedDate
        ? parseISO(selectedDate)
        : undefined

    const defaultMonth = selected
        ?? (
            availableDates.length > 0
                ? parseISO(availableDates[0])
                : new Date()
        )

    const isAvailable = (date: Date) =>
        availableDates.includes(
            format(date, "yyyy-MM-dd"),
        )

    useEffect(() => {
        const handleClickOutside = (
            event: MouseEvent,
        ) => {
            if (
                containerRef.current &&
                !containerRef.current.contains(
                    event.target as Node,
                )
            ) {
                setIsOpen(false)
            }
        }

        document.addEventListener(
            "mousedown",
            handleClickOutside,
        )

        return () => {
            document.removeEventListener(
                "mousedown",
                handleClickOutside,
            )
        }
    }, [])

    return (
        <div
            className="date-picker-wrapper"
            ref={containerRef}
        >
            <button
                type="button"
                className="date-picker-trigger"
                onClick={() =>
                    setIsOpen((current) => !current)
                }
                disabled={
                    availableDates.length === 0
                }
            >
                <span>
                    {selectedDate || "Select date"}
                </span>

                <span aria-hidden="true">
                    📅
                </span>
            </button>

            {isOpen && (
                <div className="date-picker-popover">
                    <DayPicker
                        mode="single"
                        selected={selected}
                        defaultMonth={defaultMonth}
                        onSelect={(date) => {
                            if (!date) {
                                return
                            }

                            const value = format(
                                date,
                                "yyyy-MM-dd",
                            )

                            onDateChange(value)
                            setIsOpen(false)
                        }}
                        disabled={(date) =>
                            !isAvailable(date)
                        }
                    />
                </div>
            )}
        </div>
    )
}


export default AnalysisDatePicker