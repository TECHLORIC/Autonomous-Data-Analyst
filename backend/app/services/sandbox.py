import docker
import tarfile
import io
import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class PythonSandbox:
    """
    Executes Python code in an isolated Docker container without relying on volume mounts,
    making it robust across Windows, Mac, and Linux hosts.
    """
    def __init__(self, image: str = "auto-data-analyst-sandbox:latest"):
        self.image = image
        try:
            self.client = docker.from_env()
            # Try to get the image, build if not exists
            try:
                self.client.images.get(self.image)
            except docker.errors.ImageNotFound:
                logger.info(f"Building custom sandbox image {self.image}... This may take a few minutes.")
                dockerfile = '''
                FROM python:3.11-slim
                RUN pip install --no-cache-dir pandas numpy scikit-learn scipy statsmodels
                '''
                import io
                f = io.BytesIO(dockerfile.encode('utf-8'))
                self.client.images.build(fileobj=f, tag=self.image, rm=True)
                logger.info("Sandbox image built successfully.")
        except Exception as e:
            logger.warning(f"Could not initialize Docker client: {e}")
            self.client = None

    def _create_tarball(self, script_code: str, dataset_path: str) -> bytes:
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            # Add script
            script_bytes = script_code.encode('utf-8')
            tarinfo = tarfile.TarInfo(name='script.py')
            tarinfo.size = len(script_bytes)
            tar.addfile(tarinfo, io.BytesIO(script_bytes))
            
            # Add dataset
            if dataset_path:
                with open(dataset_path, 'rb') as f:
                    dataset_bytes = f.read()
                
                # We rename the file to dataset.csv or dataset.parquet based on extension
                ext = dataset_path.split('.')[-1]
                filename = f"dataset.{ext}"
                
                tarinfo = tarfile.TarInfo(name=filename)
                tarinfo.size = len(dataset_bytes)
                tar.addfile(tarinfo, io.BytesIO(dataset_bytes))
                
        tar_stream.seek(0)
        return tar_stream.read()

    def execute(self, code: str, dataset_path: str = "") -> Dict[str, Any]:
        """
        Executes arbitrary python code.
        The code is expected to write its structured output to 'result.json'.
        """
        if not self.client:
            raise RuntimeError("Docker is not available. Sandbox execution failed.")

        container = None
        try:
            # Create a sleeping container
            container = self.client.containers.create(
                image=self.image,
                command="sleep 60",
                working_dir="/workspace",
                network_disabled=True, # Prevent external network access
                mem_limit="512m",      # Restrict memory
                detach=True
            )
            container.start()

            # Upload files
            tar_data = self._create_tarball(code, dataset_path)
            container.put_archive("/workspace", tar_data)

            # Execute script
            exec_log = container.exec_run(
                cmd="python script.py",
                workdir="/workspace",
            )
            
            stdout = exec_log.output.decode('utf-8')
            
            # Fetch result.json
            try:
                bits, stat = container.get_archive("/workspace/result.json")
                
                # Extract file from tar stream
                tar_stream = io.BytesIO(b"".join(bits))
                with tarfile.open(fileobj=tar_stream) as tar:
                    member = tar.getmember("result.json")
                    f = tar.extractfile(member)
                    result_data = json.loads(f.read().decode('utf-8'))
                    
                return {
                    "success": exec_log.exit_code == 0,
                    "stdout": stdout,
                    "result": result_data,
                    "exit_code": exec_log.exit_code
                }
            except docker.errors.NotFound:
                # No result.json was produced
                return {
                    "success": exec_log.exit_code == 0,
                    "stdout": stdout,
                    "result": None,
                    "exit_code": exec_log.exit_code,
                    "error": "No result.json was produced by the script."
                }
                
        except Exception as e:
            logger.exception("Sandbox execution error")
            return {
                "success": False,
                "stdout": "",
                "result": None,
                "error": str(e),
                "exit_code": -1
            }
        finally:
            if container:
                try:
                    container.remove(force=True)
                except:
                    pass
