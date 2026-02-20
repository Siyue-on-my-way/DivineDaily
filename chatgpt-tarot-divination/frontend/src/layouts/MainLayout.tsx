import { ReactNode, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useGlobalState } from '@/store'
import { useIsMobile } from '@/hooks'

interface MainLayoutProps {
    children: ReactNode
}

export default function MainLayout({ children }: MainLayoutProps) {
    const isMobile = useIsMobile()
    const { isDark, settings } = useGlobalState()

    useEffect(() => {
        if (isDark) {
            document.documentElement.classList.add('dark')
        } else {
            document.documentElement.classList.remove('dark')
        }
    }, [isDark])

    const showAd = !isMobile && settings.ad_client && settings.ad_slot

    useEffect(() => {
        if (showAd && settings.fetched) {
            try {
                // @ts-ignore
                ; (window.adsbygoogle = window.adsbygoogle || []).push({})
                    // @ts-ignore
                    ; (window.adsbygoogle = window.adsbygoogle || []).push({})
            } catch (e) {
                console.error('AdSense error:', e)
            }
        }
    }, [showAd, settings.fetched])

    return (
        <div className="min-h-screen bg-gradient-to-br from-background via-muted/10 to-primary/5 text-foreground overflow-x-hidden selection:bg-primary/30">
            {/* Mystical Background Decorations */}
            <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
                <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-primary/10 rounded-full blur-[100px] animate-pulse" />
                <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-secondary/10 rounded-full blur-[80px] animate-pulse delay-1000" />
            </div>

            <div className="w-full px-4 md:px-8 py-4 md:py-6">
                <div className="grid grid-cols-1 md:grid-cols-6 gap-6">

                    {/* Left Ad Column */}
                    {showAd && (
                        <div className="hidden md:block md:col-span-1">
                            <ins
                                className="adsbygoogle sticky top-4"
                                style={{ display: 'block', minHeight: '600px' }}
                                data-ad-client={settings.ad_client}
                                data-ad-slot={settings.ad_slot}
                                data-ad-format="auto"
                                data-full-width-responsive="true"
                            ></ins>
                        </div>
                    )}

                    {/* Main Content Area */}
                    <div className={`flex flex-col min-h-[calc(100vh-3rem)] ${showAd ? 'md:col-span-4' : 'md:col-span-6'}`}>

                        {/* Page Content with unified width constraint */}
                        <main className="flex-1 relative pt-4 md:pt-6">
                            <div className="max-w-4xl mx-auto w-full">
                                <AnimatePresence mode="wait">
                                    {children}
                                </AnimatePresence>
                            </div>
                        </main>

                        <footer className="mt-8 py-6 text-center text-sm text-muted-foreground border-t border-border/40">
                            <p>© {new Date().getFullYear()} AI Tarot Divination. Keep an open mind.</p>
                        </footer>
                    </div>

                    {/* Right Ad Column */}
                    {showAd && (
                        <div className="hidden md:block md:col-span-1">
                            <ins
                                className="adsbygoogle sticky top-4"
                                style={{ display: 'block', minHeight: '600px' }}
                                data-ad-client={settings.ad_client}
                                data-ad-slot={settings.ad_slot}
                                data-ad-format="auto"
                                data-full-width-responsive="true"
                            ></ins>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
