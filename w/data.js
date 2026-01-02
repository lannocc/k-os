import { writable } from 'svelte/store';

export const tab_main = writable(localStorage.getItem('k_tab_main') || '');
tab_main.subscribe(val => localStorage.setItem('k_tab_main', val));

export function tabs_reset() {
    tab_main.set('');
}

