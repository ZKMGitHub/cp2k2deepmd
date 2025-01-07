## Install from source code
```bash
git clone https://github.com/ZKMGitHub/cp2k2deepmd.git
cd cp2k2deepmd
pip install .
```
## Example
Using the output data from CP2K-based ab initio molecular dynamics (AIMD) simulations of portlandite crystal in the NVT ensemble as an example, stored in `./example/portlandite`.
- Define the output files and the interval for extracting frames in the `config` file (`./example/config.json`).
  ```bash
  cd ./example
  ```
- Run `run.py`
  ```bash
  python run.py
  ```
- Then we can get the output files (`./example/portlandite/deepmd`) which can be used in deepmd training
