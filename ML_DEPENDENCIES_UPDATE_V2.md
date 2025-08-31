# ML Dependencies Update V2

## Issue Addressed
The initial fix for ML dependencies failed due to compilation issues on Render's read-only filesystem:
```
error: failed to create directory `/usr/local/cargo/registry/cache/index.crates.io-1949cf8c6b5b557f`
Caused by: Read-only file system (os error 30)
```

This was caused by the `y-py` package (a JupyterLab dependency) trying to compile Rust code.

## Updated Solution
1. Modified CatBoost installation to use `--no-deps` flag:
   ```
   catboost==1.2.5 --no-deps
   ```
   This prevents CatBoost from pulling in dependencies that might require compilation.

2. Changed PyTorch to use the pre-compiled CPU-only version:
   ```
   torch==2.2.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
   ```
   This uses a pre-built binary wheel instead of trying to compile from source.

## Expected Results
After deploying these changes:
1. The installation should complete without compilation errors
2. CatBoost and PyTorch should be available for ML functionality
3. The warnings about missing ML dependencies should no longer appear

## Deployment Instructions
1. The updated requirements.txt has been pushed to GitHub
2. Redeploy the application on Render
3. Monitor logs to confirm successful installation
4. Verify ML functionality is working correctly

## Notes
- Using `--no-deps` with CatBoost means we're relying on the dependencies already installed by other packages
- The CPU-only version of PyTorch is sufficient for inference and basic training
- If you need GPU support, you'll need to use a different deployment strategy
