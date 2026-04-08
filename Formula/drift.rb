class Driftshell < Formula
  desc "Local CLI: plain English → shell commands via Ollama"
  homepage "https://github.com/a-elhaag/driftshell"
  url "https://github.com/a-elhaag/driftshell/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "332307afcdb2dc633a0ec245fa3700d87307eb8af41a0865ffdf6d24eca314b0"
  license "MIT"

  depends_on "python@3.11"

  # pydantic-core ships prebuilt .so wheels whose load-command headers have no
  # room for Homebrew's install_name_tool relinking pass.  Skip it for the venv.
  skip_clean "libexec"

  def install
    # Create virtual environment
    venv = libexec / "venv"
    system Formula["python@3.11"].bin / "python3.11", "-m", "venv", venv

    # Install driftshell (non-editable so paths are stable)
    system venv / "bin" / "pip", "install", "--upgrade", "pip"
    system venv / "bin" / "pip", "install", "--no-build-isolation", "."

    # Wrapper scripts for both entry points
    (bin / "drift").write_env_script(venv / "bin" / "drift", {})
    (bin / "d").write_env_script(venv / "bin" / "d", {})
  end

  test do
    system bin / "drift", "--version"
  end
end
