# Upload this update to the existing GitHub repository

Repository: https://github.com/davis-twinomugisha/wsn_lab1

Extract the ZIP and copy the contents of its wsn_lab1 folder into your existing local checkout.
Keep any unrelated local files. Review `git status` and the changed files before committing.
Upload the extracted files, not just the ZIP archive, if using GitHub's web upload interface.
The final report files belong in docs/.

For an existing configured checkout, run from its root:

```bash
git status
git add README.md GITHUB_UPDATE.md requirements.txt python data figures docs
git diff --cached --stat
git commit -m "Update sensor analysis and final report from Arduino recording"
git push
```

The prepared update does not change the two original firmware sketches or claim a new hardware test.
