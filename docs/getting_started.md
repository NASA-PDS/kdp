# Getting Started TODO/WIP

This introductory guide will introduce the key concepts in KDP pipelines, and will give a clear understanding of the necessary steps you must take when adoping KDP as their pipeline orchestrator.

KDP is short for *kubernetes does pipelines*, or (more fun): *KDP does pipelines*. This is because, in short, *KDP is an extension of the kubernetes API*. Through use of the [operator pattern](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/), KDP extends the functionality of the kubernetes API, adding its pipeline definition and execution on top of kubernetes' industry-leading container orchestration, lifecycle management, and scalability. As such, KDP *doesn't actually execute your code* - it simply hands it off to kubernetes and takes care of some connecting-of-dots, if you will.

So, what exactly is a *pipeline* in KDP? Simple: in KDP, a pipeline is any process that takes input, applies any number of *sequential* processing steps to it, and spits out some output at the end. This could be as simple as converting an image from JPEG to PNG, to as complex as gathering input from a streaming source, processing it, validating it, then finally archiving it - all in real time. 

In KDP, pipelines are modeled as *[directed acyclic graphs](https://en.wikipedia.org/wiki/Directed_acyclic_graph)*. The most notable criteria for DAGs in KDP are that they:

 - Have a single starting ([root](https://en.wikipedia.org/wiki/Glossary_of_graph_theory#root)) node
 - Contain only [directed edges](https://en.wikipedia.org/wiki/Glossary_of_graph_theory#direction)
 - Do not contain any [cycles](https://en.wikipedia.org/wiki/Cycle_(graph_theory))

KDP imposes these constraints on pipelines so that certain properties can be inferred through graph theory. For example, these constraints are the sole reason KDP can detect when a pipeline should spin down - the conditions for "doneness" (i.e. all data have propagated through the entire pipeline) are well understood and *provable*. (TODO)

## Key Concepts

We've taken a cursory glance at pipelines, but how are they constructed? Recall that a pipeline is defined as taking an input, performing some processing steps, then providing an output. KDP maps a key architectural concept to each of these:

 - *DataInputs* handle pipeline input;
 - *Pipelines* handle arbirary processing steps; and
 - *DataOutputs* handle pipeline output (TODO in later release)

The rest of this guide introduces each of these concepts in detail, as all three must be implemented for a pipeline to be complete.