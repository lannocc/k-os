<script>
    import { onMount } from 'svelte';

    let images;

    onMount(async () => {
        k_on_message(on_k);
        await k_call('art');
    });

    async function on_k(msg) {
        if ('images' in msg) {
            let names = [ ];
            let last;

            for (let image of msg.images) {
                if (!/^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}/.test(image))
                    continue;

                if (image.endsWith('_combined')) {
                    image = image.slice(0, -9);
                    names.push([ image, false, true ]);
                    last = image;
                }
                else {
                    if (last && last == image) {
                        names[names.length-1][1] = true;
                    }
                    else {
                        names.push([ image, true, false ]);
                    }
                    last = false;
                }
            }

            images = names;
        }
    }
</script>


<h2>Ack Images</h2>

{#if images}
    <section>
      {#each images as image}
        <div class=mask>
          {#if image[1]}
            <a href=/a/{image[0]}.png target=_new title="Open in new tab">
                <img src=/a/{image[0]}.png/>
            </a>
          {/if}
        </div>
        <div class=details>
            {image[0]}
        </div>
        <div class=composite>
          {#if image[2]}
            <a href=/a/{image[0]}_combined.png target=_new
               title="Open in new tab">
                <img src=/a/{image[0]}_combined.png/>
            </a>
          {/if}
        </div>
      {/each}
    </section>
{/if}


<style>
    section {
        display: grid;
        grid-gap: 9px;
        grid-template-columns: 39% 21% 39%;
        grid-template-areas: "mask details composite";
    }

    section img {
        width: 95%;
        border: 3px solid #666;
    }

    /* FIXME...
    .mask {
        grid-area: mask;
    }

    .details {
        grid-area: details;
    }

    .composite {
        grid-area: composite;
    }
     */

    .mask img {
        box-shadow: 3px 3px 3px #996;
    }

    .composite img {
        box-shadow: -3px 3px 3px #996;
    }

    :global(html.theme) .mask img {
        box-shadow: 3px 3px 3px #336;
    }

    :global(html.theme) .composite img {
        box-shadow: -3px 3px 3px #336;
    }
</style>

