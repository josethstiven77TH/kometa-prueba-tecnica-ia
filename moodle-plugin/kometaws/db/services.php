<?php
defined('MOODLE_INTERNAL') || die();

$functions = [
    'local_kometaws_create_section' => [
        'classname'   => 'local_kometaws\external\create_section',
        'methodname'  => 'execute',
        'description' => 'Crea o actualiza una sección de un curso con nombre y resumen',
        'type'        => 'write',
        'ajax'        => false,
    ],
    'local_kometaws_create_resource' => [
        'classname'   => 'local_kometaws\external\create_resource',
        'methodname'  => 'execute',
        'description' => 'Crea un recurso (archivo) dentro de una sección de un curso',
        'type'        => 'write',
        'ajax'        => false,
    ],
];

$services = [
    'Kometa WS' => [
        'functions' => [
            'local_kometaws_create_section',
            'local_kometaws_create_resource',
        ],
        'restrictedusers' => 0,
        'enabled' => 1,
    ],
];
