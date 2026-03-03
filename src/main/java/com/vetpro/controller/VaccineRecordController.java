package com.vetpro.controller;

import com.vetpro.model.VaccineRecord;
import com.vetpro.service.VaccineRecordService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/api/vaccine-records")
public class VaccineRecordController {

    private final VaccineRecordService vaccineRecordService;

    public VaccineRecordController(VaccineRecordService vaccineRecordService) {
        this.vaccineRecordService = vaccineRecordService;
    }

    @PostMapping
    public ResponseEntity<VaccineRecord> administerVaccine(@Valid @RequestBody VaccineRecord vaccineRecord) {
        VaccineRecord created = vaccineRecordService.administerVaccine(vaccineRecord);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @GetMapping("/pet/{petId}")
    public ResponseEntity<List<VaccineRecord>> getByPet(@PathVariable Long petId) {
        return ResponseEntity.ok(vaccineRecordService.getRecordsByPet(petId));
    }

    @GetMapping("/overdue")
    public ResponseEntity<List<VaccineRecord>> getOverdue(@RequestParam LocalDate date) {
        return ResponseEntity.ok(vaccineRecordService.getOverdueVaccinations(date));
    }
}
