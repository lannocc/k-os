<script>
    import { onMount, tick } from 'svelte';
    import { tab_main, tabs_reset } from './data.js';
    import { read_global_var } from './py.js';
    import About from './About.svelte';
    import Art from './Art.svelte';
    import Video from './Video.svelte';
    //import Replay from './Replay.svelte';

    const tabs = {
        //'About': About,
        'Art': Art,
        'Video': Video,
        //'Replay': Replay,
    };

    let showing = false;
    let pending = new Set();

    let pws = '(unknown)';
    let pws_class = '';

    onMount(async () => {
        k_on_message(on_k, 1);

        //FIXME: a better way for this...
        if ('' === new URLSearchParams(document.location.search).get('kick')) {
            //active = About;
            tabs_reset();
            document.location.search = '';
        }

        const ver = await read_global_var('../version.py', 'VVHEN');
        document.getElementById('version').textContent = 'v/ ' + ver;

        const status = k_status();
        pws = status[0];
        pws_class = status[1];
    })

    async function on_k(msg) {
    }

    async function activate(tab) {
        if ($tab_main == tab) {
            $tab_main = '_';
            await tick();
        }
        $tab_main = tab;
    }
</script>


<header>
    <aside>
        <div>
            Python WebSocket Status:
            <div id=pws class={pws_class}>{pws}</div>
        </div>
    </aside>

    <nav>
      {#each Object.entries(tabs) as [ name, comp ]}
        <button type=button on:click={async () => activate(name)}
                class:active={$tab_main==name}>{name}</button>
      {/each}
    </nav>
</header>

<main>
  {#if $tab_main}
    <svelte:component this={tabs[$tab_main]}/>
  {:else}
    <svelte:component this={About}/>
  {/if}
</main>


<style>
    header aside {
        position: absolute;
        top: 1em;
        right: 1em;
        text-align: right;
        font-size: smaller;
    }

    header aside > div {
        margin-bottom: 1em;
    }

    header aside .link {
        font-size: larger;
    }

    header aside .pending {
        background-color: yellow ! important;
    }

    header aside ul, header aside li {
        display: block;
        list-style: none;
        margin: 0;
        padding: 0;
    }

    header aside li {
        display: inline-block;
        padding: .2em;
    }

    header aside table {
        background-color: #FFF9FF;
    }

    header nav {
        text-align: center;
    }

    main {
        text-align: center;
        padding: 1em;
        margin: 0 auto;
    }

    @media screen {
        :global(html.theme) header aside table {
            background-color: #321;
        }

        :global(html.theme) header aside .pending {
            background-color: darkorange ! important;
        }
     }

    @media print {
        main {
            padding: 0;
            margin: 0;
            max-width: 100vw;
            overflow: visible;
        }
    }
</style>

