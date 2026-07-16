<?php
namespace local_kometaws\external;

defined('MOODLE_INTERNAL') || die();

global $CFG;
require_once($CFG->dirroot . '/course/modlib.php');
require_once($CFG->libdir . '/resourcelib.php');

use core_external\external_api;
use core_external\external_function_parameters;
use core_external\external_value;
use core_external\external_single_structure;

class create_resource extends external_api {

    public static function execute_parameters() {
        return new external_function_parameters([
            'courseid'    => new external_value(PARAM_INT, 'ID del curso'),
            'sectionnum'  => new external_value(PARAM_INT, 'Número de sección (0 = general)'),
            'name'        => new external_value(PARAM_TEXT, 'Nombre del recurso'),
            'intro'       => new external_value(PARAM_RAW, 'Descripción del recurso', VALUE_DEFAULT, ''),
            'draftitemid' => new external_value(PARAM_INT, 'itemid del área de borrador donde está el archivo subido'),
        ]);
    }

    public static function execute($courseid, $sectionnum, $name, $intro, $draftitemid) {
        global $DB;

        $params = self::validate_parameters(self::execute_parameters(), [
            'courseid'    => $courseid,
            'sectionnum'  => $sectionnum,
            'name'        => $name,
            'intro'       => $intro,
            'draftitemid' => $draftitemid,
        ]);

        $course = $DB->get_record('course', ['id' => $params['courseid']], '*', MUST_EXIST);
        $context = \context_course::instance($course->id);
        self::validate_context($context);
        require_capability('moodle/course:manageactivities', $context);

        $moduleinfo = new \stdClass();
        $moduleinfo->modulename   = 'resource';
        $moduleinfo->module       = $DB->get_field('modules', 'id', ['name' => 'resource']);
        $moduleinfo->course       = $course->id;
        $moduleinfo->section      = $params['sectionnum'];
        $moduleinfo->name         = $params['name'];
        $moduleinfo->intro        = $params['intro'];
        $moduleinfo->introformat  = FORMAT_HTML;
        $moduleinfo->introeditor  = ['text' => $params['intro'], 'format' => FORMAT_HTML, 'itemid' => 0];
        $moduleinfo->visible      = 1;
        $moduleinfo->files        = $params['draftitemid'];
        $moduleinfo->display      = \RESOURCELIB_DISPLAY_AUTO;
        $moduleinfo->showsize     = 0;
        $moduleinfo->showtype     = 0;
        $moduleinfo->showdate     = 0;
        $moduleinfo->groupmode    = $course->groupmode;
        $moduleinfo->groupingid   = 0;
        $moduleinfo->completion   = 0;
        $moduleinfo->visibleoncoursepage = 1;

        $created = create_module($moduleinfo);

        return [
            'cmid' => $created->coursemodule,
            'id'   => $created->instance,
        ];
    }

    public static function execute_returns() {
        return new external_single_structure([
            'cmid' => new external_value(PARAM_INT, 'ID del course module creado'),
            'id'   => new external_value(PARAM_INT, 'ID de la instancia del recurso'),
        ]);
    }
}
