<script>
    import { onMount } from 'svelte';
    import { read_global_var } from './py.js';

    let info;
    let extra;

    onMount(async () => {
        info = await read_global_var('../k/home.py', 'INFO');
        extra = await read_global_var('../k/home.py', 'EXTRA');
    });

</script>


<!--<h2>About K</h2>-->

{#if info}
    <section>{info}</section>
{/if}
{#if extra}
    <section>{extra}</section>
{/if}


<style>
    section {
        text-align: left;
        white-space: pre-wrap;
        margin-top: 1em;
        margin-left: auto;
        margin-right: auto;
        max-width: 600px;
    }
</style>

