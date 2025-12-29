<script>
    export let video;

    let playing;

    function play() {
        playing = true;
    }
</script>


{#if video}
  <section>
    <aside class=id>
        <p><em>Video ID</em>: <b>{video.id}</b></p>
    </aside>
  {#if playing}
    <video src=/d/{video.cytid}/{video.ytid}.18.mp4 autoplay controls/>
  {:else}
    <img on:click={play} src=/d/{video.cytid}/{video.ytid}.jpg/>
  {/if}
    <div>
        <p><em>Title</em>: <b>{video.title}</b></p>
        <p><em>URL</em>:
            <b><a href=https://youtu.be/{video.ytid} target=_new
                  title='Open in new tab'>https://youtu.be/{video.ytid}</a></b>
        </p>
        <p><em>YTID</em>: <b>{video.ytid}</b></p>
    </div>
  </section>
{/if}


<style>
    section {
        margin: .5em;
        padding: .5em;
        background-color: #FED;
        text-align: left;
    }

    aside {
        float: right;
        background-color: #DEF;
        padding: .5em;
        font-family: serif;
        font-size: larger;
        clear: right;
    }

    aside.id {
        font-size: small;
    }

    aside.id p {
        margin: 0;
    }

    aside.fav {
        margin-top: .5em;
    }

    aside button {
        display: block;
        font-size: small;
    }

    img, video {
        display: inline-block;
        max-width: 100%;
        vertical-align: middle;
        cursor: pointer;
    }

    div {
        display: inline-block;
    }

    @media screen {
        :global(html.theme) section {
            background-color: #012;
        }

        :global(html.theme) aside {
            background-color: #210;
        }
    }

    @media print {
        aside {
            background: none;
            text-decoration: underline;
            font-style: italic;
        }

        aside button {
            display: none;
        }
    }
</style>

