# Notes on Generative Diffusion Models, Part 1: DDPM = Demolition + Construction <!-- {docsify-ignore-all} -->

> Original author: Su Jianlin. Source: [the original Chinese article on Scientific Spaces](https://kexue.fm/archives/9119), published on 2022-06-13. This English version is a translation prepared for this website for study; the original article's perspective and historical context are preserved.
>
> Last reviewed on this website: 2026-10-01. This is the date of the site's content maintenance, not the date of the original article. Descriptions of model development reflect the original publication date, and external links have not all been individually verified. The original republication and citation information is retained at the end.

When it comes to generative models, [VAEs](https://kexue.fm/tag/vae/) and [GANs](https://kexue.fm/tag/GAN/) are household names, and the original author's blog has discussed them many times. There are also some less mainstream choices, such as [flow models](https://kexue.fm/tag/flow/) and [VQ-VAE](https://kexue.fm/archives/6760), which have attracted considerable interest. In particular, VQ-VAE and its variant [VQ-GAN](https://arxiv.org/abs/2012.09841) have recently begun to serve as "image tokenizers," making it possible to apply a range of NLP pretraining methods directly to images. Alongside these models, another previously more obscure option—diffusion models—is rapidly gaining ground in generative modeling. The two leading text-to-image systems at the time of writing, OpenAI's [DALL·E 2](https://arxiv.org/abs/2204.06125) and Google's [Imagen](https://arxiv.org/abs/2205.11487), both use diffusion models.

<!-- [![Some of Imagen's text-to-image examples](https://kexue.fm/usr/uploads/2022/06/2782509104.jpg)](https://kexue.fm/usr/uploads/2022/06/2782509104.jpg "View the original image") -->

<img src="https://kexue.fm/usr/uploads/2022/06/2782509104.jpg" alt="Some of Imagen's text-to-image examples" style="width:100%;max-width:800px;">

<!-- <img>Some of Imagen's text-to-image examples</img> -->

This article begins a new series introducing some of the progress in generative diffusion models over the preceding two years. These models are said to be mathematically complex, apparently much harder to understand than VAEs or GANs. Is that really the case? Is a plain-language understanding of diffusion models impossible? Let us find out.

## A New Starting Point

The original author's earlier articles, ["GANs from an Energy Perspective, Part 3: Generative Models = Energy Models"](https://kexue.fm/archives/6612) and ["From Denoising Autoencoders to Generative Models"](https://kexue.fm/archives/7038), briefly introduced diffusion models. Most articles about diffusion models mention energy-based models, score matching, Langevin equations, and related concepts. In brief, techniques such as score matching train an energy model, and a Langevin equation is then used to sample from it.

Theoretically, this is a well-established approach that can, in principle, generate and sample any continuous object, including speech and images. In practice, however, training the energy function is difficult, especially for high-dimensional data such as high-resolution images: it is hard to learn a sufficiently complete energy function. Sampling from an energy model through a Langevin equation also involves considerable uncertainty and often produces noisy results. For a long time, diffusion models following this traditional approach were therefore tested only on relatively low-resolution images.

The current surge of interest in generative diffusion models began with [DDPM](https://arxiv.org/abs/2006.11239), the Denoising Diffusion Probabilistic Model proposed in 2020. Although it also uses the name "diffusion model," DDPM is, apart from certain similarities in the form of its sampling procedure, quite different from traditional diffusion models that sample using Langevin equations. It represents a new starting point and a new chapter.

In the author's view, "gradual transformation model" would describe DDPM more accurately; the name "diffusion model" can be misleading. Concepts from traditional diffusion models, such as energy models, score matching, and Langevin equations, are not needed for the treatment of DDPM and its subsequent variants given here. Interestingly, DDPM's mathematical framework had already been established in the ICML 2015 paper ["Deep Unsupervised Learning using Nonequilibrium Thermodynamics"](https://arxiv.org/abs/1503.03585). DDPM was the first to make that framework work for high-resolution image generation, which prompted the subsequent enthusiasm. The emergence and popularity of a model often require both time and opportunity.

## Demolition and Construction

Many introductions to DDPM immediately bring in transition distributions and then variational inference. The ensuing mathematical notation can scare readers away. Such presentations also reveal that DDPM is, in fact, a VAE rather than a diffusion model in the traditional sense. Combined with readers' existing impressions of traditional diffusion models, this creates the illusion that advanced mathematics is essential. Yet DDPM also admits a plain-language interpretation; it is no harder to grasp than a GAN with its familiar "counterfeiter versus inspector" analogy.

First, suppose we want a generative model like a GAN. Its task is to transform random noise $\boldsymbol{z}$ into a data sample $\boldsymbol{x}$:

$$
\begin{equation}\require{AMScd}\begin{CD}
\text{Random noise}\boldsymbol{z}\quad @>\quad\text{Transformation}\quad>> \quad\text{Data sample}\boldsymbol{x}\\
@V \text{Analogy} VV  @VV \text{Analogy} V\\
\text{Bricks and cement}\quad @>\quad\text{Construction}\quad>> \quad\text{Building}\\
\end{CD}\end{equation}
$$

<!-- [![Call me an engineer](https://kexue.fm/usr/uploads/2022/06/403506617.jpeg)](https://kexue.fm/usr/uploads/2022/06/403506617.jpeg "View the original image") -->
<!-- <img src="https://kexue.fm/usr/uploads/2022/06/403506617.jpeg" alt="Call me an engineer" style="width:100%;max-width:400px;align-self:center"> -->

We can think of this process as construction. Random noise $\boldsymbol{z}$ is the raw material—bricks, tiles, and cement—while the data sample $\boldsymbol{x}$ is a finished building. The generative model is a construction crew that turns the raw material into a building.

This is certainly difficult, which is why generative models have inspired so much research. But, as the saying goes, destruction is easier than construction. You may not know how to build a building, but you can probably work out how to demolish one. Consider the process of taking a building apart, step by step, into bricks, tiles, and cement. Let $\boldsymbol{x}_0$ be the finished building, or data sample, and let $\boldsymbol{x}_T$ be the materials left after demolition, or random noise. If demolition takes $T$ steps, the entire process is

$$
\begin{equation}\boldsymbol{x} = \boldsymbol{x}_0 \to \boldsymbol{x}_1 \to \boldsymbol{x}_2 \to \cdots \to \boldsymbol{x}_{T-1} \to \boldsymbol{x}_T = \boldsymbol{z}\end{equation}
$$

Building is difficult because the leap from raw material $\boldsymbol{x}_T$ to a finished building $\boldsymbol{x}_0$ is so large. It is hard to see how $\boldsymbol{x}_T$ could become $\boldsymbol{x}_0$ all at once. Once we have the intermediate demolition stages $\boldsymbol{x}_1,\boldsymbol{x}_2,\cdots,\boldsymbol{x}_T$, however, we know that $\boldsymbol{x}_{t-1} \to \boldsymbol{x}_t$ is one demolition step. Reversing it, $\boldsymbol{x}_t\to \boldsymbol{x}_{t-1}$, is therefore one construction step. If we can learn the transformation $\boldsymbol{x}_{t-1}=\boldsymbol{\mu}(\boldsymbol{x}_t)$, we can start from $\boldsymbol{x}_T$ and repeatedly apply $\boldsymbol{x}_{T-1}=\boldsymbol{\mu}(\boldsymbol{x}_T)$, $\boldsymbol{x}_{T-2}=\boldsymbol{\mu}(\boldsymbol{x}_{T-1})$, and so on, until we obtain the finished building $\boldsymbol{x}_0$.

## How to Demolish a Building

Just as a meal is eaten one bite at a time, a building must be constructed one step at a time. DDPM follows exactly this demolition-and-construction analogy. It first works in the opposite direction, defining a process that gradually transforms a data sample into random noise. It then considers the reverse transformation and generates data by applying that reverse transformation repeatedly. This is why the article suggested that "gradual transformation model" might be a more accurate description of DDPM than "diffusion model."

Specifically, DDPM models demolition as

$$
\begin{equation}\boldsymbol{x}_t = \alpha_t \boldsymbol{x}_{t-1} + \beta_t \boldsymbol{\varepsilon}_t,\quad \boldsymbol{\varepsilon}_t\sim\mathcal{N}(\boldsymbol{0}, \boldsymbol{I})\label{eq:forward}\end{equation}
$$

Here $\alpha_t,\beta_t > 0$ and $\alpha_t^2 + \beta_t^2=1$. Usually $\beta_t$ is very close to zero and represents the amount of damage to the existing structure in a single demolition step. Introducing noise $\boldsymbol{\varepsilon}_t$ corrupts the original signal. We can also think of this noise as raw material: each step turns $\boldsymbol{x}_{t-1}$ into "a remaining structure $\alpha_t \boldsymbol{x}_{t-1}$ plus raw material $\beta_t \boldsymbol{\varepsilon}_t$." (**Note:** The definitions of $\alpha_t,\beta_t$ in this article differ from those in the original paper.)

Repeating this demolition step gives

$$
\begin{equation}\begin{aligned}
\boldsymbol{x}_t =&\, \alpha_t \boldsymbol{x}_{t-1} + \beta_t \boldsymbol{\varepsilon}_t \\
=&\, \alpha_t \big(\alpha_{t-1} \boldsymbol{x}_{t-2} + \beta_{t-1} \boldsymbol{\varepsilon}_{t-1}\big) + \beta_t \boldsymbol{\varepsilon}_t \\
=&\,\cdots\\
=&\,(\alpha_t\cdots\alpha_1) \boldsymbol{x}_0 + \underbrace{(\alpha_t\cdots\alpha_2)\beta_1 \boldsymbol{\varepsilon}_1 + (\alpha_t\cdots\alpha_3)\beta_2 \boldsymbol{\varepsilon}_2 + \cdots + \alpha_t\beta_{t-1} \boldsymbol{\varepsilon}_{t-1} + \beta_t \boldsymbol{\varepsilon}_t}_{\text{Sum of independent Gaussian noise terms}}
\end{aligned}\label{eq:expand}\end{equation}
$$

You may already have wondered why the mixing coefficients must satisfy $\alpha_t^2 + \beta_t^2 = 1$. We can now answer that question. First, the part marked by the brace is a sum of independent Gaussian noise terms. Their means are zero and their variances are $(\alpha_t\cdots\alpha_2)^2\beta_1^2$, $(\alpha_t\cdots\alpha_3)^2\beta_2^2$, ..., $\alpha_t^2\beta_{t-1}^2$, and $\beta_t^2$. Next, we use a fact from probability theory: a sum of independent Gaussian random variables is itself Gaussian. The sum above therefore has mean zero and variance $(\alpha_t\cdots\alpha_2)^2\beta_1^2 + (\alpha_t\cdots\alpha_3)^2\beta_2^2 + \cdots + \alpha_t^2\beta_{t-1}^2 + \beta_t^2$. Finally, because $\alpha_t^2 + \beta_t^2 = 1$ holds at every step, the sum of the squared coefficients in $\eqref{eq:expand}$ is still one:

$$
\begin{equation}(\alpha_t\cdots\alpha_1)^2 + (\alpha_t\cdots\alpha_2)^2\beta_1^2 + (\alpha_t\cdots\alpha_3)^2\beta_2^2 + \cdots + \alpha_t^2\beta_{t-1}^2 + \beta_t^2 = 1\end{equation}
$$

This means we can equivalently write

$$
\begin{equation}\boldsymbol{x}_t = \underbrace{(\alpha_t\cdots\alpha_1)}_{\text{Denoted by }\bar{\alpha}_t} \boldsymbol{x}_0 + \underbrace{\sqrt{1 - (\alpha_t\cdots\alpha_1)^2}}_{\text{Denoted by }\bar{\beta}_t} \bar{\boldsymbol{\varepsilon}}_t,\quad \bar{\boldsymbol{\varepsilon}}_t\sim\mathcal{N}(\boldsymbol{0}, \boldsymbol{I})\label{eq:skip}\end{equation}
$$

This makes computing $\boldsymbol{x}_t$ much easier. DDPM also chooses an appropriate form for $\alpha_t$ so that $\bar{\alpha}_T\approx 0$. After $T$ demolition steps, the remaining structure is therefore negligible: almost everything has become raw material $\boldsymbol{\varepsilon}$. (**Note:** The definition of $\bar{\alpha}_t$ in this article differs from that in the original paper.)

## How to Build It Again

Demolition maps $\boldsymbol{x}_{t-1}\to \boldsymbol{x}_t$ and gives us many data pairs $(\boldsymbol{x}_{t-1},\boldsymbol{x}_t)$. Construction naturally means learning a model that maps $\boldsymbol{x}_t\to \boldsymbol{x}_{t-1}$ from those pairs. If we denote that model by $\boldsymbol{\mu}(\boldsymbol{x}_t)$, an obvious training objective is to minimize the Euclidean distance between the two:

$$
\begin{equation}\left\Vert\boldsymbol{x}_{t-1} - \boldsymbol{\mu}(\boldsymbol{x}_t)\right\Vert^2\label{eq:loss-0}\end{equation}
$$

We are already very close to the final DDPM model. Let us refine this process a little. First, the demolition equation $\eqref{eq:forward}$ can be rewritten as $\boldsymbol{x}_{t-1} = \frac{1}{\alpha_t}\left(\boldsymbol{x}_t  - \beta_t \boldsymbol{\varepsilon}_t\right)$. This suggests giving our construction model $\boldsymbol{\mu}(\boldsymbol{x}_t)$ the form

$$
\begin{equation}\boldsymbol{\mu}(\boldsymbol{x}_t) = \frac{1}{\alpha_t}\left(\boldsymbol{x}_t   - \beta_t \boldsymbol{\epsilon}_{\boldsymbol{\theta}}(\boldsymbol{x}_t, t)\right)\label{eq:sample}\end{equation}
$$

where $\boldsymbol{\theta}$ denotes the trainable parameters. Substituting it into the loss function gives

$$
\begin{equation}\left\Vert\boldsymbol{x}_{t-1} - \boldsymbol{\mu}(\boldsymbol{x}_t)\right\Vert^2 = \frac{\beta_t^2}{\alpha_t^2}\left\Vert \boldsymbol{\varepsilon}_t - \boldsymbol{\epsilon}_{\boldsymbol{\theta}}(\boldsymbol{x}_t, t)\right\Vert^2\end{equation}
$$

The factor $\frac{\beta_t^2}{\alpha_t^2}$ is a loss weight, which we can ignore for the moment. Finally, combining $\eqref{eq:skip}$ and $\eqref{eq:forward}$ gives the following expression for $\boldsymbol{x}_t$:

$$
\begin{equation}\boldsymbol{x}_t = \alpha_t\boldsymbol{x}_{t-1} + \beta_t \boldsymbol{\varepsilon}_t = \alpha_t\left(\bar{\alpha}_{t-1}\boldsymbol{x}_0 + \bar{\beta}_{t-1}\bar{\boldsymbol{\varepsilon}}_{t-1}\right) + \beta_t \boldsymbol{\varepsilon}_t = \bar{\alpha}_t\boldsymbol{x}_0 + \alpha_t\bar{\beta}_{t-1}\bar{\boldsymbol{\varepsilon}}_{t-1} + \beta_t \boldsymbol{\varepsilon}_t \end{equation}
$$

The loss function becomes

$$
\begin{equation}\left\Vert \boldsymbol{\varepsilon}_t - \boldsymbol{\epsilon}_{\boldsymbol{\theta}}(\bar{\alpha}_t\boldsymbol{x}_0 + \alpha_t\bar{\beta}_{t-1}\bar{\boldsymbol{\varepsilon}}_{t-1} + \beta_t \boldsymbol{\varepsilon}_t, t)\right\Vert^2\label{eq:loss-1}\end{equation}
$$

You may wonder why we went back one step to express $\boldsymbol{x}_t$. Could we obtain $\boldsymbol{x}_t$ directly from $\eqref{eq:skip}$? No: we have already sampled $\boldsymbol{\varepsilon}_t$, and $\boldsymbol{\varepsilon}_t$ and $\bar{\boldsymbol{\varepsilon}}_t$ are not independent. Given $\boldsymbol{\varepsilon}_t$, we cannot sample $\bar{\boldsymbol{\varepsilon}}_t$ independently of it.

## Reducing Variance

In principle, the loss function $\eqref{eq:loss-1}$ is sufficient to train DDPM. In practice, however, its variance may be too high, leading to slow convergence and other problems. To see why, observe that $\eqref{eq:loss-1}$ contains four random variables that need to be sampled:

> 1. Sample a $\boldsymbol{x}_0$ from the training data.
>
> 2. Sample $\bar{\boldsymbol{\varepsilon}}_{t-1}, \boldsymbol{\varepsilon}_t$ from $\mathcal{N}(\boldsymbol{0}, \boldsymbol{I})$ (two distinct samples).
>
> 3. Sample a $t$ from $1\sim T$.

The more random variables we need to sample, the harder it is to estimate the loss accurately. Equivalently, each estimate fluctuates more: its variance is higher. Fortunately, an integration trick lets us combine $\bar{\boldsymbol{\varepsilon}}_{t-1}, \boldsymbol{\varepsilon}_t$ into a single Gaussian random variable and thereby reduce the variance.

The trick requires some care, but it is not particularly complicated. Because sums of independent Gaussian variables are Gaussian, $\alpha_t\bar{\beta}_{t-1}\bar{\boldsymbol{\varepsilon}}_{t-1} + \beta_t \boldsymbol{\varepsilon}_t$ is equivalent to a single random variable $\bar{\beta}_t\boldsymbol{\varepsilon}|\boldsymbol{\varepsilon}\sim \mathcal{N}(\boldsymbol{0}, \boldsymbol{I})$. Likewise, $\beta_t \bar{\boldsymbol{\varepsilon}}_{t-1} - \alpha_t\bar{\beta}_{t-1} \boldsymbol{\varepsilon}_t$ is equivalent to a single random variable $\bar{\beta}_t\boldsymbol{\omega}|\boldsymbol{\omega}\sim \mathcal{N}(\boldsymbol{0}, \boldsymbol{I})$. We can verify that $\mathbb{E}[\boldsymbol{\varepsilon}\boldsymbol{\omega}^{\top}]=\boldsymbol{0}$, so these two Gaussian random variables are independent.

Next, express $\boldsymbol{\varepsilon}_t$ in terms of $\boldsymbol{\varepsilon},\boldsymbol{\omega}$:

$$
\begin{equation}\boldsymbol{\varepsilon}_t = \frac{(\beta_t \boldsymbol{\varepsilon} - \alpha_t\bar{\beta}_{t-1} \boldsymbol{\omega})\bar{\beta}_t}{\beta_t^2 + \alpha_t^2\bar{\beta}_{t-1}^2} = \frac{\beta_t \boldsymbol{\varepsilon} - \alpha_t\bar{\beta}_{t-1} \boldsymbol{\omega}}{\bar{\beta}_t}\end{equation}
$$

Substituting this into $\eqref{eq:loss-1}$ gives

$$
\begin{equation}\begin{aligned}
&\,\mathbb{E}_{\bar{\boldsymbol{\varepsilon}}_{t-1}, \boldsymbol{\varepsilon}_t\sim \mathcal{N}(\boldsymbol{0}, \boldsymbol{I})}\left[\left\Vert \boldsymbol{\varepsilon}_t - \boldsymbol{\epsilon}_{\boldsymbol{\theta}}(\bar{\alpha}_t\boldsymbol{x}_0 + \alpha_t\bar{\beta}_{t-1}\bar{\boldsymbol{\varepsilon}}_{t-1} + \beta_t \boldsymbol{\varepsilon}_t, t)\right\Vert^2\right] \\
=&\,\mathbb{E}_{\boldsymbol{\omega}, \boldsymbol{\varepsilon}\sim \mathcal{N}(\boldsymbol{0}, \boldsymbol{I})}\left[\left\Vert \frac{\beta_t \boldsymbol{\varepsilon} - \alpha_t\bar{\beta}_{t-1} \boldsymbol{\omega}}{\bar{\beta}_t} - \boldsymbol{\epsilon}_{\boldsymbol{\theta}}(\bar{\alpha}_t\boldsymbol{x}_0 + \bar{\beta}_t\boldsymbol{\varepsilon}, t)\right\Vert^2\right]
\end{aligned}\end{equation}
$$

The loss is now only quadratic in $\boldsymbol{\omega}$, so we can expand it and compute its expectation directly. The result is

$$
\begin{equation}\frac{\beta_t^2}{\bar{\beta}_t^2}\mathbb{E}_{\boldsymbol{\varepsilon}\sim \mathcal{N}(\boldsymbol{0}, \boldsymbol{I})}\left[\left\Vert\boldsymbol{\varepsilon} - \frac{\bar{\beta}_t}{\beta_t}\boldsymbol{\epsilon}_{\boldsymbol{\theta}}(\bar{\alpha}_t\boldsymbol{x}_0 + \bar{\beta}_t\boldsymbol{\varepsilon}, t)\right\Vert^2\right]+\text{constant}\end{equation}
$$

Dropping the constant and the loss weight once more, we obtain the loss function ultimately used by DDPM:

$$
\begin{equation}\left\Vert\boldsymbol{\varepsilon} - \frac{\bar{\beta}_t}{\beta_t}\boldsymbol{\epsilon}_{\boldsymbol{\theta}}(\bar{\alpha}_t\boldsymbol{x}_0 + \bar{\beta}_t\boldsymbol{\varepsilon}, t)\right\Vert^2\end{equation}
$$

(**Note:** The original paper's $\boldsymbol{\epsilon}_{\boldsymbol{\theta}}$ is actually $\frac{\bar{\beta}_t}{\beta_t}\boldsymbol{\epsilon}_{\boldsymbol{\theta}}$ in this article's notation, so the two results are identical.)

## Recursive Generation

We have now worked through DDPM's entire training procedure. There has been a fair amount to explain, so it would be a stretch to call it easy. Yet there is almost nothing especially difficult: we have used neither traditional energy functions and score matching nor even variational inference. The demolition-and-construction analogy, together with some basic probability theory, gives exactly the same result. Emerging generative diffusion models such as DDPM are therefore less complicated than many readers imagine. They model the familiar way we learn by taking things apart and putting them back together.

After training, we can generate a sample by starting from random noise $\boldsymbol{x}_T\sim\mathcal{N}(\boldsymbol{0}, \boldsymbol{I})$ and executing $T$ steps of $\eqref{eq:sample}$:

$$
\begin{equation}\boldsymbol{x}_{t-1} = \frac{1}{\alpha_t}\left(\boldsymbol{x}_t - \beta_t \boldsymbol{\epsilon}_{\boldsymbol{\theta}}(\boldsymbol{x}_t, t)\right)\end{equation}
$$

This corresponds to greedy search in autoregressive decoding. For random sampling, we need to add a noise term:

$$
\begin{equation}\boldsymbol{x}_{t-1} = \frac{1}{\alpha_t}\left(\boldsymbol{x}_t - \beta_t \boldsymbol{\epsilon}_{\boldsymbol{\theta}}(\boldsymbol{x}_t, t)\right) + \sigma_t \boldsymbol{z},\quad \boldsymbol{z}\sim\mathcal{N}(\boldsymbol{0}, \boldsymbol{I})\end{equation}
$$

In general, we can set $\sigma_t=\beta_t$, keeping the forward and reverse variances aligned. This sampling procedure differs from Langevin sampling in traditional diffusion models. Each DDPM sample starts from random noise and requires $T$ iterations to produce a single output. Langevin sampling starts from an arbitrary point and iterates indefinitely; theoretically, all data samples are generated over that infinite sequence of iterations. Beyond a similarity in form, these are therefore two fundamentally different models.

This generation procedure also resembles Seq2Seq decoding: both generate autoregressively through a sequence of dependent steps. Generation speed is consequently a bottleneck. DDPM sets $T=1000$, meaning that generating a single image requires evaluating $\boldsymbol{\epsilon}_{\boldsymbol{\theta}}(\boldsymbol{x}_t, t)$ 1,000 times. Slow sampling is one of DDPM's major drawbacks, and much subsequent work has focused on accelerating it. The combination of image generation, autoregressive modeling, and slow speed may remind some readers of early models such as [PixelRNN](https://arxiv.org/abs/1601.06759) and [PixelCNN](https://arxiv.org/abs/1606.05328). These cast image generation as a language-modeling task, so they too generate recursively and slowly. What, then, is the substantive difference between DDPM's autoregressive generation and that of PixelRNN/PixelCNN? Why did DDPM become so popular while PixelRNN/PixelCNN did not?

Readers familiar with PixelRNN/PixelCNN know that these models generate an image one pixel at a time. Because autoregressive generation is ordered, we must first choose an order for the image's pixels, and the resulting quality is closely tied to that order. At present, this ordering can only be designed manually using experience—such design choices are collectively called inductive biases—and there is no known theoretically optimal solution. In other words, inductive bias strongly affects the generation quality of PixelRNN/PixelCNN. DDPM takes a different approach: it defines a new autoregressive direction through demolition, while treating all pixels equally rather than imposing a pixel order. This reduces the influence of that inductive bias and improves the results. Furthermore, DDPM uses a fixed number of generation steps $T$, whereas PixelRNN/PixelCNN require a number proportional to the image resolution ($\text{width}\times\text{height}\times{\text{number of channels}}$). DDPM therefore generates high-resolution images much faster than PixelRNN/PixelCNN.

## Hyperparameter Choices

This section considers the choice of hyperparameters.

DDPM uses $T=1000$, which may be much larger than many readers would expect. Why choose such a large $T$? Meanwhile, translating the original paper's choice of $\alpha_t$ into the notation of this article gives approximately

$$
\begin{equation}\alpha_t = \sqrt{1 - \frac{0.02t}{T}}\end{equation}
$$

This is a monotonically decreasing function. Why should $\alpha_t$ decrease monotonically?

The two questions have similar answers, both related to the nature of the data. For simplicity, we used the Euclidean distance $\eqref{eq:loss-0}$ as the reconstruction loss. DDPM is usually used to generate images, and readers with experience in image generation know that Euclidean distance is not a good measure of realism. VAEs trained to reconstruct images with Euclidean distance often produce blurry results. Clearer results are possible when the input and output images are very close to one another. Choosing a large $T$ makes each input and output pair as similar as possible, reducing the blurring associated with Euclidean distance.

Choosing a monotonically decreasing $\alpha_t$ follows a similar argument. When $t$ is small, $\boldsymbol{x}_t$ is still close to a real image, so we want a small difference between $\boldsymbol{x}_{t-1}$ and $\boldsymbol{x}_t$ to make Euclidean distance $\eqref{eq:loss-0}$ more appropriate. We therefore use a larger $\alpha_t$. When $t$ is large, $\boldsymbol{x}_t$ is already close to pure noise. Euclidean distance works adequately for noise, so we can increase the difference between $\boldsymbol{x}_{t-1}$ and $\boldsymbol{x}_t$ slightly by using a smaller $\alpha_t$. Could we simply use a large $\alpha_t$ throughout? Yes, but then we would need a larger $T$. Recall that, when deriving $\eqref{eq:skip}$, we required $\bar{\alpha}_T\approx 0$. We can estimate it directly:

$$
\begin{equation}\log \bar{\alpha}_T = \sum_{t=1}^T \log\alpha_t = \frac{1}{2} \sum_{t=1}^T \log\left(1 - \frac{0.02t}{T}\right) < \frac{1}{2} \sum_{t=1}^T \left(- \frac{0.02t}{T}\right) = -0.005(T+1)\end{equation}
$$

Substituting $T=1000$ gives roughly $\bar{\alpha}_T\approx e^{-5}$, which is just small enough for the $\approx 0$ criterion. If we keep $\alpha_t$ large throughout, we necessarily need a larger $T$ to make $\bar{\alpha}_T\approx 0$.

Finally, notice that the construction model $\boldsymbol{\epsilon}_{\boldsymbol{\theta}}(\bar{\alpha}_t\boldsymbol{x}_0 + \bar{\beta}_t\boldsymbol{\varepsilon}, t)$ explicitly takes $t$ as an input. In principle, different values of $t$ correspond to objects at different stages, so each stage should have its own reconstruction model: we would need $T$ distinct models. Instead, we share their parameters and pass $t$ as a conditioning input. According to the paper's appendix, $t$ is converted into a positional encoding of the kind described in ["The Road to Better Transformers, Part 1: Tracing the Origins of Sinusoidal Positional Encoding"](https://kexue.fm/archives/8231) and then added directly to the residual blocks.

## Summary

This article has introduced the then-new generative diffusion model DDPM through the accessible analogy of demolishing and constructing a building. From this perspective, plain-language explanations and relatively little mathematics lead to exactly the same result as the original paper. Like a GAN, DDPM has a vivid analogy that makes it easier to understand. Its derivation here needs neither the variational machinery of VAEs nor the probability divergences and optimal transport used in GANs. In that sense, DDPM can even be considered simpler than a VAE or a GAN.

---

_**When republishing, include the original article's address:** [https://kexue.fm/archives/9119](https://kexue.fm/archives/9119 "Notes on Generative Diffusion Models, Part 1: DDPM = Demolition + Construction")_

_**For more detailed republication guidance, see:**_ ["Scientific Spaces FAQ"](https://kexue.fm/archives/6508#%E6%96%87%E7%AB%A0%E5%A6%82%E4%BD%95%E8%BD%AC%E8%BD%BD/%E5%BC%95%E7%94%A8 "Scientific Spaces FAQ")

**If you enjoyed the original article, you are welcome to [share it](https://kexue.fm/archives/9119#share) or [tip the original author](https://kexue.fm/archives/9119#pay). The author explains that tips are intended as a way to understand readers' interest in Scientific Spaces rather than as a source of income. Ignoring this invitation does not affect your ability to read the article. The original author welcomes and thanks readers for their support.**

**To cite the original Chinese article, use:**

Su Jianlin. (Jun. 13, 2022). 《生成扩散模型漫谈（一）：DDPM = 拆楼 + 建楼 》\[Blog post\]. Retrieved from [https://kexue.fm/archives/9119](https://kexue.fm/archives/9119)

@online{kexuefm-9119,  
        title={生成扩散模型漫谈（一）：DDPM = 拆楼 + 建楼},  
        author={苏剑林},  
        year={2022},  
        month={Jun},  
        url={\\url{https://kexue.fm/archives/9119}},  
}
