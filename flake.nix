{
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.flake-compat = {
    url = "github:edolstra/flake-compat";
    flake = false;
  };
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-22.11";
  inputs.poetry2nix = {
    url = "github:nix-community/poetry2nix";
    inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils, flake-compat, poetry2nix }:
    {
      overlay = nixpkgs.lib.composeManyExtensions [
        poetry2nix.overlay
        (final: prev: {
          myapp = prev.poetry2nix.mkPoetryApplication { projectDir = ./.; };
        })
      ];
    } // (flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ self.overlay ];
        };
      in
      {
        defaultPackage = pkgs.myapp;

        devShell =
          pkgs.mkShell { buildInputs = with pkgs; [ python3 poetry black ]; };

        nixosModules.default = with pkgs.lib;
          { config, ... }:
          let cfg = config.services.form2slides-shuffle;
          in
          {
            options.services.form2slides-shuffle = {
              enable = mkEnableOption "Enable Form2Slides shuffle service";
            };
            config = {
              systemd.services.form2slides-shuffle = {
                serviceConfig = {
                  Type = "simple";
                  ExecStart =
                    "${self.defaultPackage.${system}}/bin/form2slides-shuffle";
                  StateDirectory = "form2slides";
                  WorkingDirectory = "/var/lib/form2slides";
                  DynamicUser = true;

                  NoNewPrivileges = true;
                  PrivateTmp = true;
                  PrivateDevices = true;
                  ProtectSystem = "strict";
                  ProtectHome = true;
                  ProtectControlGroups = true;
                  ProtectKernelModules = true;
                  ProtectKernelTunables = true;
                  RestrictAddressFamilies =
                    [ "AF_UNIX" "AF_INET" "AF_INET6" "AF_NETLINK" ];
                  RestrictRealtime = true;
                  RestrictNamespaces = true;
                  MemoryDenyWriteExecute = true;
                };
                wantedBy = [ "multi-user.target" ];
                after = [ "network.target" ];
              };
            };
          };
      }));
}
