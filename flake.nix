{
  description = "Hello world flake using uv2nix";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    { self, nixpkgs, uv2nix, pyproject-nix, pyproject-build-systems, ... }:
    let
      inherit (nixpkgs) lib;
      workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };
      overlay = workspace.mkPyprojectOverlay { sourcePreference = "wheel"; };
      pyprojectOverrides = _final: _prev: { };
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
      python = pkgs.python312;
      pythonSet = (pkgs.callPackage pyproject-nix.build.packages {
        inherit python;
      }).overrideScope (lib.composeManyExtensions [
        pyproject-build-systems.overlays.default
        overlay
        pyprojectOverrides
      ]);
    in {
      packages.x86_64-linux.default =
        (pythonSet.mkVirtualEnv "wireguard-mesh-coordinator"
          workspace.deps.default).overrideAttrs (old: {
            venvIgnoreCollisions = [ "*" ];
            buildInputs = (old.buildInputs or [ ]) ++ [ pkgs.wireguard-tools ];
            propagatedBuildInputs = (old.propagatedBuildInputs or [ ])
              ++ [ pkgs.wireguard-tools ];
          });

      apps.x86_64-linux = {
        wireguard-mesh-coordinator = {
          type = "app";
          program = pkgs.writeScriptBin "wireguard-mesh-coordinator" ''
            export PATH=${pkgs.wireguard-tools}/bin:$PATH
            exec ${self.packages.x86_64-linux.default}/bin/wireguard-mesh-coordinator "$@"
          '';
        };
      };
    };
}
