from app_accesos_residencial import get_mock_data, render_personas

if __name__ == "__main__":
    eventos_mock, personas_mock, vehiculos_mock, policies_mock = get_mock_data()
    render_personas(eventos_mock, personas_mock, vehiculos_mock, policies_mock)
