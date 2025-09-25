'use client'

import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'

export default function Test() {
  const [connectionStatus, setConnectionStatus] = useState('Verificando...')
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    const testConnection = async () => {
      try {
        // Probar conexión básica
        const { data, error } = await supabase.from('_test').select('*').limit(1)
        
        if (error && error.code !== 'PGRST116') {
          setConnectionStatus('Error de conexión: ' + error.message)
        } else {
          setConnectionStatus('✅ Conexión a Supabase exitosa')
        }

        // Obtener usuario actual
        const { data: { user } } = await supabase.auth.getUser()
        setUser(user)
      } catch (err) {
        setConnectionStatus('❌ Error: ' + err)
      }
    }

    testConnection()
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold mb-4">Prueba de Conexión Supabase</h1>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-2">Estado de Conexión:</h2>
          <p className="text-gray-700">{connectionStatus}</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow mt-4">
          <h2 className="text-lg font-semibold mb-2">Usuario Actual:</h2>
          {user ? (
            <div>
              <p><strong>Email:</strong> {user.email}</p>
              <p><strong>ID:</strong> {user.id}</p>
              <p><strong>Última conexión:</strong> {new Date(user.last_sign_in_at).toLocaleString()}</p>
            </div>
          ) : (
            <p>No hay usuario autenticado</p>
          )}
        </div>
      </div>
    </div>
  )
}
