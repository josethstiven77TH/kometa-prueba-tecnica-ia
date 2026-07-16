<?php
namespace local_kometaws\external;

defined('MOODLE_INTERNAL') || die();

global $CFG;
require_once($CFG->dirroot . '/course/lib.php');

use core_external\external_api;
use core_external\external_function_parameters;
use core_external\external_value;
use core_external\external_single_structure;

class create_section extends external_api {

    public static function execute_parameters() {
        return new external_function_parameters([
            'courseid'   => new external_value(PARAM_INT, 'ID del curso'),
            'sectionnum' => new external_value(PARAM_INT, 'Número de sección a crear/actualizar'),
            'name'       => new external_value(PARAM_TEXT, 'Nombre de la sección'),
            'summary'    => new external_value(PARAM_RAW, 'Resumen/descripción de la sección', VALUE_DEFAULT, ''),
        ]);
    }

    public static function execute($courseid, $sectionnum, $name, $summary) {
        global $DB;

        $params = self::validate_parameters(self::execute_parameters(), [
            'courseid'   => $courseid,
            'sectionnum' => $sectionnum,
            'name'       => $name,
            'summary'    => $summary,
        ]);

        $course = $DB->get_record('course', ['id' => $params['courseid']], '*', MUST_EXIST);
        $context = \context_course::instance($course->id);
        self::validate_context($context);
        require_capability('moodle/course:update', $context);

        course_create_sections_if_missing($course, $params['sectionnum']);

        $section = $DB->get_record('course_sections', [
            'course'  => $course->id,
            'section' => $params['sectionnum'],
        ], '*', MUST_EXIST);

        $data = new \stdClass();
        $data->id = $section->id;
        $data->name = $params['name'];
        $data->summary = $params['summary'];
        $data->summaryformat = FORMAT_HTML;

        course_update_section($course, $section, $data);

        return ['sectionid' => $section->id];
    }

    public static function execute_returns() {
        return new external_single_structure([
            'sectionid' => new external_value(PARAM_INT, 'ID de la sección'),
        ]);
    }
}
