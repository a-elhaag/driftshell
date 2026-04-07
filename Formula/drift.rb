class Drift < Formula
  desc "Local CLI: plain English → shell commands via Ollama"
  homepage "https://github.com/a-elhaag/driftshell"
  url "https://github.com/a-elhaag/driftshell/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "placeholder_sha256"
  license "MIT"

  depends_on "python@3.11"

  def install
    # Create virtual environment
    venv = libexec / "venv"
    system Formula["python@3.11"].bin / "python3", "-m", "venv", venv

    # Install driftshell
    system venv / "bin" / "pip", "install", "--upgrade", "pip"
    system venv / "bin" / "pip", "install", "-e", "."

    # Create wrapper script
    (bin / "drift").write_env_script(venv / "bin" / "drift", {})
  end

  test do
    system bin / "drift", "--version"
  end
end
