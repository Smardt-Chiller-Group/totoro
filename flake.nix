{
  description = "Totoro DevOps Tool Development Environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
      pythonPackages = pkgs.python311Packages;
    in {
      devShells.x86_64-linux.default = pkgs.mkShell {
        buildInputs = [
          pkgs.python311
          pythonPackages.pip
          pythonPackages.setuptools
          
          # Azure CLI for container registry authentication
          pkgs.azure-cli
          
          # Docker CLI (if not already installed system-wide)
          pkgs.docker
          
          # Git (for git operations in totoro)
          pkgs.git
          
          # Development tools
          pkgs.uv
        ];

        shellHook = ''
          echo "🎬 Totoro DevOps Environment"
          echo "=============================="
          
          # Ensure we're using Python 3.11
          export PYTHON="${pkgs.python311}/bin/python3.11"
          
          # Create virtual environment if it doesn't exist
          if [ ! -d ".venv" ]; then
            echo "Creating Python virtual environment..."
            $PYTHON -m venv .venv
            source .venv/bin/activate
            # Unset PYTHONPATH to prevent Nix packages from being imported leading to version issues
            unset PYTHONPATH
            echo "Installing totoro in editable mode..."
            pip install -e .
          else
            source .venv/bin/activate
            # Unset PYTHONPATH to prevent Nix packages from being imported leading to version issues
            unset PYTHONPATH
          fi
          
          echo ""
          echo "✓ Virtual environment activated"
          echo "✓ Python version: $(python --version)"
          echo "✓ Azure CLI available: $(az --version | head -n1)"
          echo "✓ Totoro commands ready to use"
          echo ""
          echo "Try: totoro --help"
          echo ""
        '';
      };
    };
}
