import K from './K.svelte';
//import Debug from './Debug.svelte';

const web = new K({
    target: document.getElementById('svapp'),
    props: {
        //active: Debug,
    }
});

export default web;

