<script>
    import { onMount } from 'svelte';
    import Channel from './video/Channel.svelte';
    import Video from './video/Video.svelte';

    let channels;
    let _channel;
    let videos;

    onMount(async () => {
        k_on_message(on_k);
        await k_call('video');
    });

    async function on_k(msg) {
        if ('channels' in msg) {
            channels = msg.channels;
        }
        else if ('videos' in msg) {
            videos = msg.videos;
        }
    }

    async function show_channel(channel) {
        if (_channel && _channel.id == channel.id) {
            _channel = false;
            videos = false;
        }
        else {
            _channel = channel;
            await k_call('video', { channel: channel.id });
        }
    }
</script>


<h2>Video Downloads</h2>

{#if channels}
    <ul>
      {#each channels as channel}
        <li>
            <button on:click={async () => show_channel(channel)}
                    class:active={_channel && _channel.id == channel.id}
                    class=link>{channel.name}</button>

          {#if _channel && _channel.id == channel.id}
            <Channel {channel}/>
            {#if videos}
                <section>
                  {#each videos as video}
                    <Video {video}/>
                  {/each}
                </section>
            {/if}
          {/if}
        </li>
      {/each}
    </ul>
{/if}


<style>
    ul, li {
        display: block;
        list-style: none;
        margin: 0;
        padding: 0;
    }

    li {
        margin: .1em;
    }

    section {
        border: 3px solid green;
    }
</style>

