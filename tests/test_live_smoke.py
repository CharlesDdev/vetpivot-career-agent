from vetpivot import live_smoke


def test_live_smoke_reports_missing_credentials_without_running_live_checks(monkeypatch, capsys):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    monkeypatch.setattr("sys.argv", ["vetpivot-live-smoke"])

    exit_code = live_smoke.main()

    captured = capsys.readouterr()
    assert exit_code == live_smoke.MISSING_CREDENTIALS_EXIT_CODE
    assert "Missing live credentials" in captured.err
    assert "Live readiness:" in captured.out


def test_live_smoke_readiness_only_does_not_print_secret_values(monkeypatch, capsys):
    monkeypatch.setenv("GEMINI_API_KEY", "test-secret")
    monkeypatch.setattr("sys.argv", ["vetpivot-live-smoke", "--readiness-only"])

    exit_code = live_smoke.main()

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "GEMINI_API_KEY set: True" in captured.out
    assert "test-secret" not in captured.out


def test_live_smoke_reports_unexpected_sdk_errors_without_traceback(monkeypatch, capsys):
    monkeypatch.setenv("GEMINI_API_KEY", "test-secret")
    monkeypatch.setattr("sys.argv", ["vetpivot-live-smoke"])
    monkeypatch.setattr(live_smoke, "_run_gemini_workflow_smoke", lambda _: None)
    monkeypatch.setattr(live_smoke, "_run_api_smoke", lambda _: None)

    def failing_adk_smoke(_):
        raise ValueError("model unavailable")

    monkeypatch.setattr(live_smoke, "_run_adk_smoke", failing_adk_smoke)

    exit_code = live_smoke.main()

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Live smoke failed: model unavailable" in captured.err
    assert "Traceback" not in captured.err
