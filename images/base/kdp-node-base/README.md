# kdp-node-base

This is the base image for KDP nodes. It includes the KDP manager utility to handle input and calling custom code.

# Using this container

All KDP pipeline steps must use this container as a baseline in their Dockerfile:

```
FROM kdp-node-base:latest
```

This will ensure that KDP's critical `manager` utility is configured and running in the background. Users with needs that cannot be met with the centos base can certainly implement their own base image, so long as it runs the `manager` in the same manner as found here. 

# More docs TODO