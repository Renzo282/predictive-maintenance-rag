'use client'

import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import { useRouter } from 'next/navigation'

export default function Home() {
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const getUser = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      setUser(user)
      setLoading(false)
    }
    getUser()
  }, [])

  const handleSignOut = async () => {
    await supabase.auth.signOut()
    setUser(null)
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Cargando...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                Sistema de Gestión de Mantenimiento
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              {user ? (
                <>
                  <span className="text-sm text-gray-700">
                    Bienvenido, {user.email}
                  </span>
                  <button
                    onClick={handleSignOut}
                    className="bg-red-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-red-700"
                  >
                    Cerrar Sesión
                  </button>
                </>
              ) : (
                <button
                  onClick={() => router.push('/auth')}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
                >
                  Iniciar Sesión
                </button>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Panel Principal
            </h2>
            <p className="text-lg text-gray-600 mb-8">
              Sistema de gestión de mantenimiento e incidencias
            </p>
            
            {user && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-lg shadow">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Incidencias
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Gestiona las incidencias de mantenimiento
                  </p>
                  <button
                    onClick={() => router.push('/incidencias')}
                    className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
                  >
                    Ver Incidencias
                  </button>
                </div>
                
                <div className="bg-white p-6 rounded-lg shadow">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Administración
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Panel de administración del sistema
                  </p>
                  <button
                    onClick={() => router.push('/admin')}
                    className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700"
                  >
                    Administrar
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}