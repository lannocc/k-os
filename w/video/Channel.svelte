<script>
    export let channel;
</script>


{#if channel}
  <section>
    <aside class=id>
        <p><em>Channel ID</em>: <b>{channel.id}</b></p>
    </aside>
    <p><em>Name</em>: <b>{channel.name}</b></p>
    <p><em>URL</em>:
        <b><a href={channel.url} target=_new
              title='Open in new tab'>{channel.url}</a></b>
    </p>
    <p><em>YTID</em>: <b>{channel.ytid}</b></p>
  </section>
{/if}


<style>
    section {
        width: fit-content;
        margin: .5em auto .5em auto;
        padding: .5em;
        background-color: #FED;
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

