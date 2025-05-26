import subprocess
import sys
import os

def run_command(cmd, check=True):
    print(f"> {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error ejecutando comando:\n{result.stderr}")
        sys.exit(1)
    return result.stdout.strip()

def minikube_is_running():
    output = run_command("minikube status --format '{{.Host}}'", check=False)
    return output == "Running"

def main():
    if not minikube_is_running():
        print("Minikube no está corriendo. Iniciando minikube...")
        run_command("minikube start")
    else:
        print("Minikube ya está corriendo.")

    # Aplica todos los archivos YAML en la carpeta k8s/
    k8s_folder = "Kubernetes"
    if not os.path.isdir(k8s_folder):
        print(f"No se encontró la carpeta '{k8s_folder}'. Crea esa carpeta y mete ahí tus archivos YAML.")
        sys.exit(1)

    yaml_files = [f for f in os.listdir(k8s_folder) if f.endswith(".yaml") or f.endswith(".yml")]

    if not yaml_files:
        print(f"No hay archivos YAML en la carpeta '{k8s_folder}'.")
        sys.exit(1)

    for yaml in yaml_files:
        print(f"Aplicando archivo {yaml}...")
        run_command(f"kubectl apply -f {os.path.join(k8s_folder, yaml)}")

    print("\nEstado actual de los pods:")
    pods = run_command("kubectl get pods")
    print(pods)

if __name__ == "__main__":
    main()

