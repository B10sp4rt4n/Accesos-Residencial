from app_accesos_residencial import get_mock_data, render_eventos_live

if __name__ == "__main__":
    eventos_mock, personas_mock, vehiculos_mock, policies_mock = get_mock_data()
    render_eventos_live(eventos_mock, personas_mock, vehiculos_mock, policies_mock)
