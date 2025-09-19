"""
Script de prueba para verificar todos los requerimientos funcionales
"""
import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:3000/api/v1/grinding-peru"

class GrindingPeruTester:
    """Tester para verificar funcionalidades de Grinding Perú"""
    
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = {}
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def login(self, username: str, password: str) -> bool:
        """Probar inicio de sesión"""
        try:
            logger.info(f"Probando login con usuario: {username}")
            
            login_data = {
                "username": username,
                "password": password
            }
            
            async with self.session.post(f"{BASE_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    self.test_results["login"] = "✅ PASS"
                    logger.info("Login exitoso")
                    return True
                else:
                    self.test_results["login"] = f"❌ FAIL - Status: {response.status}"
                    logger.error(f"Error en login: {response.status}")
                    return False
                    
        except Exception as e:
            self.test_results["login"] = f"❌ ERROR - {str(e)}"
            logger.error(f"Error en login: {e}")
            return False
    
    async def test_user_management(self) -> bool:
        """Probar gestión de usuarios y roles"""
        try:
            logger.info("Probando gestión de usuarios...")
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Obtener usuarios
            async with self.session.get(f"{BASE_URL}/auth/users", headers=headers) as response:
                if response.status == 200:
                    users = await response.json()
                    logger.info(f"Usuarios encontrados: {len(users)}")
                    
                    # Verificar roles
                    roles = set(user["role"] for user in users)
                    expected_roles = {"tecnico", "supervisor", "administrador"}
                    
                    if expected_roles.issubset(roles):
                        self.test_results["user_management"] = "✅ PASS"
                        return True
                    else:
                        self.test_results["user_management"] = f"❌ FAIL - Roles faltantes: {expected_roles - roles}"
                        return False
                else:
                    self.test_results["user_management"] = f"❌ FAIL - Status: {response.status}"
                    return False
                    
        except Exception as e:
            self.test_results["user_management"] = f"❌ ERROR - {str(e)}"
            logger.error(f"Error en gestión de usuarios: {e}")
            return False
    
    async def test_incident_creation(self) -> bool:
        """Probar registro de incidencias"""
        try:
            logger.info("Probando creación de incidencias...")
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            incident_data = {
                "tipo_falla": "hardware",
                "equipo_involucrado": "Servidor de Prueba",
                "ubicacion": "Data Center",
                "prioridad": "alta",
                "descripcion": "Prueba de funcionalidad del sistema",
                "fotos": ["test_photo.jpg"],
                "archivos": ["test_log.txt"]
            }
            
            async with self.session.post(f"{BASE_URL}/incidents", json=incident_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "success":
                        self.incident_id = data.get("incident_id")
                        self.test_results["incident_creation"] = "✅ PASS"
                        logger.info(f"Incidencia creada: {data.get('numero_incidencia')}")
                        return True
                    else:
                        self.test_results["incident_creation"] = f"❌ FAIL - {data.get('message')}"
                        return False
                else:
                    self.test_results["incident_creation"] = f"❌ FAIL - Status: {response.status}"
                    return False
                    
        except Exception as e:
            self.test_results["incident_creation"] = f"❌ ERROR - {str(e)}"
            logger.error(f"Error creando incidencia: {e}")
            return False
    
    async def test_incident_listing(self) -> bool:
        """Probar visualización de incidencias"""
        try:
            logger.info("Probando listado de incidencias...")
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.get(f"{BASE_URL}/incidents", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    incidents = data.get("incidents", [])
                    logger.info(f"Incidencias encontradas: {len(incidents)}")
                    
                    if len(incidents) > 0:
                        self.test_results["incident_listing"] = "✅ PASS"
                        return True
                    else:
                        self.test_results["incident_listing"] = "❌ FAIL - No hay incidencias"
                        return False
                else:
                    self.test_results["incident_listing"] = f"❌ FAIL - Status: {response.status}"
                    return False
                    
        except Exception as e:
            self.test_results["incident_listing"] = f"❌ ERROR - {str(e)}"
            logger.error(f"Error listando incidencias: {e}")
            return False
    
    async def test_incident_update(self) -> bool:
        """Probar actualización de incidencias"""
        try:
            logger.info("Probando actualización de incidencias...")
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            if not hasattr(self, 'incident_id'):
                self.test_results["incident_update"] = "❌ SKIP - No hay incidencia para actualizar"
                return False
            
            update_data = {
                "estado": "en_proceso",
                "comentarios": "Iniciando diagnóstico del problema",
                "fotos": ["diagnostico1.jpg"],
                "archivos": ["diagnostico.txt"]
            }
            
            async with self.session.put(f"{BASE_URL}/incidents/{self.incident_id}/update", 
                                      json=update_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "success":
                        self.test_results["incident_update"] = "✅ PASS"
                        logger.info("Incidencia actualizada exitosamente")
                        return True
                    else:
                        self.test_results["incident_update"] = f"❌ FAIL - {data.get('message')}"
                        return False
                else:
                    self.test_results["incident_update"] = f"❌ FAIL - Status: {response.status}"
                    return False
                    
        except Exception as e:
            self.test_results["incident_update"] = f"❌ ERROR - {str(e)}"
            logger.error(f"Error actualizando incidencia: {e}")
            return False
    
    async def test_predictive_maintenance(self) -> bool:
        """Probar módulo de predicción de fallas"""
        try:
            logger.info("Probando predicción de fallas...")
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Primero obtener equipos disponibles
            async with self.session.get(f"{BASE_URL}/maintenance/predictive-dashboard", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    equipment_list = data.get("equipment_health", [])
                    
                    if equipment_list:
                        equipment_id = equipment_list[0]["equipment_id"]
                        
                        # Probar predicción de falla
                        async with self.session.post(f"{BASE_URL}/maintenance/predict/{equipment_id}", 
                                                   headers=headers) as pred_response:
                            if pred_response.status == 200:
                                pred_data = await pred_response.json()
                                if "error" not in pred_data:
                                    self.test_results["predictive_maintenance"] = "✅ PASS"
                                    logger.info("Predicción de fallas funcionando")
                                    return True
                                else:
                                    self.test_results["predictive_maintenance"] = f"❌ FAIL - {pred_data.get('error')}"
                                    return False
                            else:
                                self.test_results["predictive_maintenance"] = f"❌ FAIL - Status: {pred_response.status}"
                                return False
                    else:
                        self.test_results["predictive_maintenance"] = "❌ SKIP - No hay equipos para probar"
                        return False
                else:
                    self.test_results["predictive_maintenance"] = f"❌ FAIL - Status: {response.status}"
                    return False
                    
        except Exception as e:
            self.test_results["predictive_maintenance"] = f"❌ ERROR - {str(e)}"
            logger.error(f"Error en predicción de fallas: {e}")
            return False
    
    async def test_maintenance_history(self) -> bool:
        """Probar historial técnico consolidado"""
        try:
            logger.info("Probando historial de mantenimiento...")
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Obtener dashboard predictivo para encontrar equipos
            async with self.session.get(f"{BASE_URL}/maintenance/predictive-dashboard", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    equipment_list = data.get("equipment_health", [])
                    
                    if equipment_list:
                        equipment_id = equipment_list[0]["equipment_id"]
                        
                        # Probar registro de mantenimiento
                        maintenance_data = {
                            "equipo_id": equipment_id,
                            "tipo_mantenimiento": "preventivo",
                            "descripcion": "Mantenimiento de prueba del sistema",
                            "materiales_utilizados": ["Aire comprimido", "Paños de limpieza"],
                            "observaciones": "Equipo funcionando correctamente",
                            "tiempo_inicio": datetime.now().isoformat(),
                            "tiempo_fin": (datetime.now() + timedelta(hours=2)).isoformat()
                        }
                        
                        async with self.session.post(f"{BASE_URL}/maintenance/record", 
                                                   json=maintenance_data, headers=headers) as maint_response:
                            if maint_response.status == 200:
                                maint_data = await maint_response.json()
                                if maint_data.get("status") == "success":
                                    self.test_results["maintenance_history"] = "✅ PASS"
                                    logger.info("Registro de mantenimiento creado exitosamente")
                                    return True
                                else:
                                    self.test_results["maintenance_history"] = f"❌ FAIL - {maint_data.get('message')}"
                                    return False
                            else:
                                self.test_results["maintenance_history"] = f"❌ FAIL - Status: {maint_response.status}"
                                return False
                    else:
                        self.test_results["maintenance_history"] = "❌ SKIP - No hay equipos para probar"
                        return False
                else:
                    self.test_results["maintenance_history"] = f"❌ FAIL - Status: {response.status}"
                    return False
                    
        except Exception as e:
            self.test_results["maintenance_history"] = f"❌ ERROR - {str(e)}"
            logger.error(f"Error en historial de mantenimiento: {e}")
            return False
    
    async def test_reports_generation(self) -> bool:
        """Probar generación de reportes automáticos"""
        try:
            logger.info("Probando generación de reportes...")
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Probar reporte de resumen de incidencias
            async with self.session.get(f"{BASE_URL}/reports/incident-summary?days=30", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if "summary" in data:
                        self.test_results["reports_generation"] = "✅ PASS"
                        logger.info("Reporte de incidencias generado exitosamente")
                        return True
                    else:
                        self.test_results["reports_generation"] = "❌ FAIL - Estructura de reporte incorrecta"
                        return False
                else:
                    self.test_results["reports_generation"] = f"❌ FAIL - Status: {response.status}"
                    return False
                    
        except Exception as e:
            self.test_results["reports_generation"] = f"❌ ERROR - {str(e)}"
            logger.error(f"Error generando reportes: {e}")
            return False
    
    async def test_admin_dashboard(self) -> bool:
        """Probar panel administrativo y auditoría"""
        try:
            logger.info("Probando panel administrativo...")
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Probar dashboard administrativo
            async with self.session.get(f"{BASE_URL}/admin/dashboard", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if "audit_metrics" in data:
                        self.test_results["admin_dashboard"] = "✅ PASS"
                        logger.info("Panel administrativo funcionando")
                        return True
                    else:
                        self.test_results["admin_dashboard"] = "❌ FAIL - Estructura de dashboard incorrecta"
                        return False
                else:
                    self.test_results["admin_dashboard"] = f"❌ FAIL - Status: {response.status}"
                    return False
                    
        except Exception as e:
            self.test_results["admin_dashboard"] = f"❌ ERROR - {str(e)}"
            logger.error(f"Error en panel administrativo: {e}")
            return False
    
    async def test_audit_logs(self) -> bool:
        """Probar logs de auditoría"""
        try:
            logger.info("Probando logs de auditoría...")
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Probar logs de auditoría
            async with self.session.get(f"{BASE_URL}/admin/audit-logs?days=30", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if "audit_logs" in data:
                        self.test_results["audit_logs"] = "✅ PASS"
                        logger.info("Logs de auditoría funcionando")
                        return True
                    else:
                        self.test_results["audit_logs"] = "❌ FAIL - Estructura de logs incorrecta"
                        return False
                else:
                    self.test_results["audit_logs"] = f"❌ FAIL - Status: {response.status}"
                    return False
                    
        except Exception as e:
            self.test_results["audit_logs"] = f"❌ ERROR - {str(e)}"
            logger.error(f"Error en logs de auditoría: {e}")
            return False
    
    async def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        logger.info("🚀 Iniciando pruebas de requerimientos funcionales para Grinding Perú")
        logger.info("=" * 80)
        
        # Probar login
        if not await self.login("admin", "admin123"):
            logger.error("❌ No se pudo hacer login. Abortando pruebas.")
            return
        
        # Ejecutar todas las pruebas
        tests = [
            ("Gestión de Usuarios y Roles", self.test_user_management),
            ("Registro de Incidencias", self.test_incident_creation),
            ("Visualización de Incidencias", self.test_incident_listing),
            ("Actualización de Incidencias", self.test_incident_update),
            ("Predicción de Fallas", self.test_predictive_maintenance),
            ("Historial de Mantenimiento", self.test_maintenance_history),
            ("Generación de Reportes", self.test_reports_generation),
            ("Panel Administrativo", self.test_admin_dashboard),
            ("Logs de Auditoría", self.test_audit_logs)
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\n📋 Probando: {test_name}")
            await test_func()
        
        # Mostrar resultados
        self.print_results()
    
    def print_results(self):
        """Mostrar resultados de las pruebas"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 RESULTADOS DE PRUEBAS - REQUERIMIENTOS FUNCIONALES")
        logger.info("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if "✅ PASS" in result)
        failed_tests = sum(1 for result in self.test_results.values() if "❌ FAIL" in result)
        error_tests = sum(1 for result in self.test_results.values() if "❌ ERROR" in result)
        skipped_tests = sum(1 for result in self.test_results.values() if "❌ SKIP" in result)
        
        for test_name, result in self.test_results.items():
            logger.info(f"{test_name.replace('_', ' ').title()}: {result}")
        
        logger.info("\n" + "-" * 80)
        logger.info(f"📈 RESUMEN:")
        logger.info(f"   Total de pruebas: {total_tests}")
        logger.info(f"   ✅ Exitosas: {passed_tests}")
        logger.info(f"   ❌ Fallidas: {failed_tests}")
        logger.info(f"   ⚠️  Errores: {error_tests}")
        logger.info(f"   ⏭️  Omitidas: {skipped_tests}")
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        logger.info(f"   📊 Tasa de éxito: {success_rate:.1f}%")
        
        if success_rate >= 80:
            logger.info("\n🎉 ¡SISTEMA FUNCIONANDO CORRECTAMENTE!")
        elif success_rate >= 60:
            logger.info("\n⚠️  Sistema funcionando con algunos problemas menores")
        else:
            logger.info("\n❌ Sistema requiere atención inmediata")
        
        logger.info("=" * 80)


async def main():
    """Función principal"""
    async with GrindingPeruTester() as tester:
        await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
