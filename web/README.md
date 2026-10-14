# nts.io

## Project organization

This workspace is organized into a simple asset structure so the project is easier to maintain.

```text
nts.io/
├── assets/
│   ├── css/
│   ├── fonts/
│   ├── images/
│   ├── js/
│   └── vendor/
├── docs/
│   └── project-structure.md
├── README.md
└── root bundled assets
```

This keeps static site files separated from source and supporting documentation while leaving the existing root-level bundled files in place to preserve compatibility.
