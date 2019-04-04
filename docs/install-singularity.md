# Singularity Install

Unlike Docker, Singularity is well suited to run in a cluster environment. In fact, if
the Docker image for this repository is provided on Docker hub, you could just pull
and use it:

```
singularity pull docker://mirabel/miracl
```

Instead, we will build it locally using a [Singularity recipe](../Singularity).

You should first [install Singularity](http://singularity.lbl.gov). If you install
the release (2.3 or below) then you will want to use bootstrap to build your image:

```
singularity create --size 8000 miracl.img
sudo singularity bootstrap miracl.img Singularity
```

If you install the development branch (2.4) then the command is just "build"

```
sudo singularity build miracl.img Singularity
```

## Interaction

To shell into the image:

```
singularity shell miracl.img
```

Bind a data directory to it

```
singularity shell -B data:/data miracl.img
```
